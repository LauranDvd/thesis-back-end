import json
import os
import sys
from urllib.request import urlopen

sys.path.append("/shared")

# sys.path.append(os.path.abspath("../shared"))

import boto3
import jwt
from dotenv import load_dotenv
from flask import Flask, request, jsonify, g
from flask_cors import CORS
from six import wraps
from sqlalchemy import create_engine

from api.TheoremQueue import TheoremQueue
from controller.ProofSearchController import ProofSearchController
from domain.EasyLogger import EasyLogger
from domain.lean.LeanInteractFacade import LeanInteractFacade
from domain.lean.MockLeanExecutor import MockLeanExecutor
from exception.LeanException import LeanException
from exception.NotFoundClientRequestException import NotFoundClientRequestException
from repository.TheoremRepository import TheoremRepository
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
            g.current_user = {"sub": "google-oauth2|115583874233243976640"}
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
                    issuer="https://" + AUTH0_DOMAIN + "/"
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

def __build_db_url(username: str, password: str, endpoint: str, port: str, db_name: str) -> str:
    return "postgresql://" + username + ":" + password + "@" + endpoint + ":" + port + "/" + db_name

def initialize():
    global lean_interact_facade, proof_search_controller, logger, theorem_proving_service

    is_test_mode = app.config.get('TESTING', False)
    print(f"Test mode: {is_test_mode}")

    if is_test_mode:
        lean_interact_facade = MockLeanExecutor()
    else:
        lean_interact_facade = MockLeanExecutor()
        # lean_interact_facade = LeanInteractFacade(test_mode=is_test_mode)

    sqs_client = boto3.client(
        'sqs',
        aws_access_key_id=os.environ['AWS_IAM_ACCESS_KEY'],
        aws_secret_access_key=os.environ['AWS_IAM_SECRET_ACCESS_KEY']
    )
    queue_url = os.environ['THEOREM_SQS_URL']
    theorem_queue = TheoremQueue(sqs_client, queue_url, EasyLogger())

    db_url = __build_db_url(os.environ["AWS_RDS_USERNAME"], os.environ["AWS_RDS_PASSWORD"],
                            os.environ['AWS_RDS_ENDPOINT'],
                            os.environ['AWS_RDS_PORT'], os.environ['AWS_RDS_DB_NAME'])
    db_engine = create_engine(db_url, pool_pre_ping=True)
    theorem_repository = TheoremRepository(db_engine, EasyLogger())

    theorem_proving_service = TheoremProvingService(
        lean_interact_facade,
        lean_interact_facade,
        theorem_queue,
        theorem_repository,
        EasyLogger()
    )
    proof_search_controller = ProofSearchController(theorem_proving_service)

    logger = EasyLogger()

@app.route('/proof', methods=['POST'])
@requires_auth
def proof():
    if request.method == 'POST':
        request_data = request.get_json()
        theorem = request_data.get("theorem")
        model_short_name = request_data.get("model")

        user_id = g.current_user.get("sub")

        try:
            proof_id = proof_search_controller.handle_post_proof(theorem, model_short_name, user_id)
            return jsonify({"proof_id": proof_id}), 202
        except NotFoundClientRequestException:
            return jsonify({}), 404
        except LeanException as e:
            return jsonify({"lean_error": str(e)}), 400

    return jsonify({}), 400


@app.route('/proof/<int:proof_id>', methods=['GET'])
@requires_auth
def get_proof_by_id(proof_id):
    user_id = g.current_user.get("sub")
    try:
        successful, found_proof = proof_search_controller.handle_get_proof(proof_id, user_id)
        return jsonify({"successful": successful, "proof": found_proof}), 200
    except NotFoundClientRequestException:
        return jsonify({}), 404


@app.route('/proof/informal/<int:proof_id>', methods=['GET'])
@requires_auth
def get_informal_proof_by_id(proof_id):
    user_id = g.current_user.get("sub")
    if request.method == 'GET':
        try:
            informal_proof, was_successful, formalized_theorem, formal_proof = proof_search_controller.handle_get_proof_informal(
                proof_id, user_id)
            return jsonify({"proof": informal_proof, "successful": was_successful,
                            "formalized_theorem": formalized_theorem, "original_proof": formal_proof}), 200
        except NotFoundClientRequestException:
            return jsonify({}), 404
    return jsonify({"error": "Bad request"}), 400


@app.route('/proof/informal', methods=['POST'])
@requires_auth
def informal_proof():
    if request.method == 'POST':
        request_data = request.get_json()
        informal_theorem = request_data.get("informal_theorem")
        model_short_name = request_data.get("model")

        user_id = g.current_user.get("sub")

        try:
            proof_id = proof_search_controller.handle_post_proof_informal(informal_theorem, model_short_name, user_id)
            return jsonify({"proof_id": proof_id}), 202
        except NotFoundClientRequestException:
            return jsonify({}), 404
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

        try:
            proof_id = proof_search_controller.handle_post_proof_fill(theorem_and_partial_proof, model_short_name,
                                                                      user_id)
            return jsonify({"proof_id": proof_id}), 202
        except NotFoundClientRequestException:
            return jsonify({}), 404
        except LeanException as e:
            return jsonify({"lean_error": str(e)}), 400
    return jsonify({"error": "Bad request"}), 400


@app.route('/proof/history', methods=['GET'])
@requires_auth
def get_proof_history():
    if request.method == 'GET':
        user_id = g.current_user.get("sub")

        proof_history = proof_search_controller.handle_get_proof_history(user_id)
        return jsonify(proof_history), 200
    return jsonify({"error": "Bad request"}), 400


@app.route('/language_model', methods=['GET'])
@requires_auth
def language_model():
    if request.method == 'GET':
        return jsonify(theorem_proving_service.get_language_model_names()), 200
    return jsonify({"error": "Bad request"}), 400


if __name__ == '__main__':
    print("will init")
    initialize()
    app.run(host='0.0.0.0', port=5000)
