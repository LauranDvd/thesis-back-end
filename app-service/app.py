import json
import os
from urllib.request import urlopen

import boto3
import jwt
import torch
from dotenv import load_dotenv
from flask import Flask, request, jsonify, g
from flask_cors import CORS
from six import wraps
from sqlalchemy import create_engine

from api.TheoremQueue import TheoremQueue
from controller.ProofSearchController import ProofSearchController
from domain.EasyLogger import EasyLogger
from domain.language_model.FormalizationLanguageModel import FormalizationLanguageModel
from domain.lean.LeanInteractFacade import LeanInteractFacade
from domain.lean.MockLeanExecutor import MockLeanExecutor
from repository.TheoremRepository import TheoremRepository
from service.FormalizationService import FormalizationService
from service.ProofSearchService import ProofSearchService
from service.TheoremProvingService import TheoremProvingService

CPU_DEVICE = "cpu"

CUDA_DEVICE = "cuda"

load_dotenv()

AUTH0_DOMAIN = os.environ['AUTH0_DOMAIN']
AUTH0_API_AUDIENCE = os.environ['AUTH0_API_AUDIENCE']
AUTH0_ALGORITHMS = [os.environ['AUTH0_ALGORITHM']]

app = Flask(__name__)
CORS(app)


class AuthError(Exception):
    def __init__(self, error, status_code):
        self.error = error
        self.status_code = status_code


@app.errorhandler(AuthError)
def handle_auth_error(exception):
    response = jsonify(exception.error)
    response.status_code = exception.status_code
    return response


def get_token_auth_header():
    auth = request.headers.get("Authorization", None)
    if not auth:
        raise AuthError({"code": "authorization_header_missing",
                         "description":
                             "Authorization header is expected"}, 401)

    auth_parts = auth.split()

    if auth_parts[0].lower() != "bearer":
        raise AuthError({"code": "invalid_header",
                         "description":
                             "Authorization header must be"
                             " Bearer token"}, 401)
    elif len(auth_parts) == 1:
        raise AuthError({"code": "invalid_header",
                         "description": "Token not found"}, 401)
    elif len(auth_parts) > 2:
        raise AuthError({"code": "invalid_header",
                         "description":
                             "Authorization header must be"
                             " Bearer token"}, 401)
    return auth_parts[1]


def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if app.config["TESTING"]:
            g.current_user = {"sub": "someone"}
            return f(*args, **kwargs)

        token = get_token_auth_header()
        jsonurl = urlopen("https://" + AUTH0_DOMAIN + "/.well-known/jwks.json")
        jwks = json.loads(jsonurl.read())
        unverified_header = jwt.get_unverified_header(token)
        public_key = None
        for key in jwks["keys"]:
            if key["kid"] == unverified_header["kid"]:
                public_key = jwt.algorithms.RSAAlgorithm.from_jwk(json.dumps(key))
        if public_key:
            try:
                payload = jwt.decode(
                    token,
                    public_key,
                    algorithms=AUTH0_ALGORITHMS,
                    audience=AUTH0_API_AUDIENCE,
                    issuer="https://"+AUTH0_DOMAIN+"/"
                )
            except jwt.ExpiredSignatureError:
                raise AuthError({"code": "token_expired",
                                "description": "token is expired"}, 401)
            except jwt.InvalidAudienceError:
                raise AuthError({"code": "invalid_audience",
                                "description":
                                    "incorrect audience,"
                                    " please check the audience"}, 401)
            except jwt.InvalidIssuerError:
                raise AuthError({"code": "invalid_issuer",
                                "description":
                                    "incorrect issuer,"
                                    " please check the issuer"}, 401)
            except Exception:
                raise AuthError({"code": "invalid_header",
                                "description":
                                    "Unable to parse authentication"
                                    " token."}, 401)

            g.current_user = payload
            return f(*args, **kwargs)
        raise AuthError({"code": "invalid_header",
                        "description": "Unable to find appropriate key"}, 401)
    return decorated


lean_interact_facade: LeanInteractFacade
proof_search_controller: ProofSearchController
logger: EasyLogger
theorem_proving_service: TheoremProvingService


def initialize():
    global lean_interact_facade, proof_search_controller, logger, theorem_proving_service

    device = CUDA_DEVICE if torch.cuda.is_available() else CPU_DEVICE
    print(f"Using device: {device}")

    # lean_interact_facade = LeanInteractFacade()
    lean_interact_facade = MockLeanExecutor()

    model_short_name_to_config = {
        # "pythia-160M":
        #     NonLoraModelAndPath(
        #         MODEL_PATHS["pythia-160M"],
        #         "EleutherAI/pythia-160m-deduped",
        #         device,
        #         lean_interact_facade,
        #         lean_interact_facade
        #     ),
        # "pythia-160M-lora":
        #     LoraModelAndPath(
        #         MODEL_PATHS["pythia-160M-lora"],
        #         "EleutherAI/pythia-160m-deduped",
        #         device,
        #         lean_interact_facade,
        #         lean_interact_facade
        #     ),
        # "pythia-410M-lora":
        #     NonLoraModelAndPath(
        #         MODEL_PATHS["pythia-410M-lora"],
        #         "EleutherAI/pythia-410m-deduped",
        #         device,
        #         lean_interact_facade,
        #         lean_interact_facade
        #     ),
    }

    formalization_language_model = FormalizationLanguageModel(
        # "deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B",
        # "deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B",
        # "EleutherAI/pythia-410m-deduped",
        # "EleutherAI/pythia-410m-deduped",
        "gpt-4.1-mini-2025-04-14",
        os.getenv('OPENAI_KEY'),
        lean_interact_facade,
        lean_interact_facade
    )

    sqs_client = boto3.client('sqs')
    queue_url = os.environ['THEOREM_SQS_URL']
    theorem_queue = TheoremQueue(sqs_client, queue_url, EasyLogger())

    db_url = "postgresql://" + os.environ["AWS_RDS_USERNAME"] + ":" + os.environ["AWS_RDS_PASSWORD"] + \
             "@" + os.environ['AWS_RDS_ENDPOINT'] + ":" + os.environ['AWS_RDS_PORT'] + "/" + \
             os.environ['AWS_RDS_DB_NAME']
    db_engine = create_engine(db_url, pool_pre_ping=True)
    theorem_repository = TheoremRepository(db_engine, EasyLogger())

    theorem_proving_service = TheoremProvingService(
        lean_interact_facade,
        lean_interact_facade,
        theorem_queue,
        theorem_repository,
        EasyLogger()
    )

    formalization_service = FormalizationService(
        formalization_language_model
    )

    proof_search_service = ProofSearchService(
        formalization_service,
        model_short_name_to_config,
        device
    )
    proof_search_controller = ProofSearchController(proof_search_service)

    logger = EasyLogger()


initialize()


@app.route('/proof', methods=['POST'])
@requires_auth
def proof():
    # if request.method == 'POST':
    #     request_data = request.get_json()
    #     theorem = request_data.get("theorem")
    #     model_short_name = request_data.get("model")
    #
    #     logger.info(f"Received theorem: {theorem}. Requested model: {model_short_name}")
    #
    #     try:
    #         generated_proof, successful = proof_search_controller.search_proof(theorem, model_short_name, True)
    #         logger.info(f"Generated proof (successful: {successful}): {generated_proof}")
    #         return jsonify({"proof": generated_proof, "successful": successful})
    #     except ValueError as e:
    #         return jsonify({"error": str(e)}), 400
    # return jsonify({"error": "Server error occurred"}), 500
    if request.method == 'POST':
        request_data = request.get_json()
        theorem = request_data.get("theorem")
        model_short_name = request_data.get("model")

        user_id = g.current_user.get("sub")

        if not theorem_proving_service.is_language_model_available(model_short_name):
            return jsonify({}), 404

        is_code_valid, lean_error = theorem_proving_service.is_lean_code_error_free(theorem)
        if not is_code_valid:
            return jsonify({"lean_error": lean_error}), 400

        # 2. send on queue, add incomplete proof to the DB
        proof_id = theorem_proving_service.send_proof_request(theorem, model_short_name, user_id)
        logger.debug(f"Proof ID for the received theorem: {proof_id}")

        return jsonify({"proof_id": proof_id}), 202
    return jsonify({}), 400


@app.route('/proof/<int:proof_id>', methods=['GET'])
@requires_auth
def get_proof_by_id(proof_id):
    successful, found_proof = theorem_proving_service.retrieve_complete_proof(proof_id)
    if found_proof is None:
        return jsonify({}), 404
    else:
        return jsonify({"successful": successful, "proof": found_proof}), 200


@app.route('/proof/informal/<int:proof_id>', methods=['GET'])
@requires_auth
def get_informal_proof_by_id(proof_id):
    informal_proof, was_successful, formalized_theorem, formal_proof = theorem_proving_service.retrieve_complete_informal_proof(
        proof_id)
    if formal_proof is None:
        return jsonify({}), 404
    else:
        return jsonify({"proof": informal_proof, "successful": was_successful,
                        "formalized_theorem": formalized_theorem, "original_proof": formal_proof}), 200


@app.route('/proof/informal', methods=['POST'])
@requires_auth
def informal_proof():
    if request.method == 'POST':
        request_data = request.get_json()
        informal_theorem = request_data.get("informal_theorem")
        model_short_name = request_data.get("model")

        user_id = g.current_user.get("sub")

        logger.info(f"Received informal theorem: {informal_theorem}. Requested model: {model_short_name}")

        if not theorem_proving_service.is_language_model_available(model_short_name):
            return jsonify({}), 404

        proof_id = theorem_proving_service.send_informal_proof_request(informal_theorem, user_id, model_short_name)
        logger.debug(f"Proof ID for the received theorem: {proof_id}")

        return jsonify({"proof_id": proof_id}), 202

        # try:
        #     informal_proof_search_result = proof_search_controller.search_informal_proof(informal_theorem, model_short_name)
        #     logger.info(
        #         f"Generated informal proof (search success: {informal_proof_search_result.was_search_successful}): {informal_proof_search_result.informal_proof}"
        #     )
        #
        #     successful = (
        #             informal_proof_search_result.was_formalization_successful and informal_proof_search_result.was_search_successful
        #             and informal_proof_search_result.was_deformalization_successful
        #     )
        #     return jsonify({
        #         "proof": informal_proof_search_result.informal_proof,
        #         "successful": successful,
        #         "formalized_theorem": informal_proof_search_result.formal_theorem,
        #         "original_proof": informal_proof_search_result.formal_proof
        #     })
        # except ValueError as e:
        #     return jsonify({"error": str(e)}), 400
    return jsonify({"error": "Bad request"}), 400


@app.route('/proof/fill', methods=['POST'])
@requires_auth
def proof_fill():
    if request.method == 'POST':
        request_data = request.get_json()
        theorem_and_partial_proof = request_data.get(
            "theorem_and_partial_proof")
        model_short_name = request_data.get("model")

        user_id = g.current_user.get("sub")

        if not theorem_proving_service.is_language_model_available(model_short_name):
            return jsonify({}), 404

        proof_id = theorem_proving_service.send_proof_fill_request(theorem_and_partial_proof, user_id, model_short_name)
        logger.debug(f"Proof ID for the received theorem: {proof_id}")

        return jsonify({"proof_id": proof_id}), 202

    #     logger.info(
    #         f"Received theorem and partial proof: {theorem_and_partial_proof}. Requested model: {model_short_name}")
    #
    #     try:
    #         generated_proof, successful = proof_search_controller.search_proof(theorem_and_partial_proof,
    #                                                                            model_short_name, False)
    #         logger.info(f"Generated proof (successful: {successful}): {generated_proof}")
    #         return jsonify({"proof": generated_proof, "successful": successful})
    #     except ValueError as e:
    #         return jsonify({"error": str(e)}), 400
    return jsonify({"error": "Bad request"}), 400


@app.route('/proof/history', methods=['GET'])
@requires_auth
def get_proof_history():
    if request.method == 'GET':
        user_id = g.current_user.get("sub")
        logger.debug(f"Getting proof history for user {user_id}")
        proof_history = theorem_proving_service.get_proof_history(user_id)
        logger.debug(f"Will return proof history of size {len(proof_history)} to user {user_id}")
        return jsonify(proof_history), 200
    return jsonify({"error": "Bad request"}), 400

@app.route('/language_model', methods=['GET'])
@requires_auth
def language_model():
    # if request.method == 'GET':
    #     return jsonify(proof_search_controller.get_language_models())
    # return jsonify({"error": "Server error occurred"}), 500
    if request.method == 'GET':
        return jsonify(theorem_proving_service.get_language_model_names()), 200
    return jsonify({"error": "Bad request"}), 400


if __name__ == '__main__':
    app.run()
