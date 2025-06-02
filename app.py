import torch
from flask import Flask, request, jsonify
from flask_cors import CORS

from config import MODEL_PATHS
from controller.ProofSearchController import ProofSearchController
from domain.EasyLogger import EasyLogger
from domain.language_model.FormalizationLanguageModel import FormalizationLanguageModel
from domain.language_model.model_configuration.LoraModelAndPath import LoraModelAndPath
from domain.language_model.model_configuration.NonLoraModelAndPath import NonLoraModelAndPath
from domain.language_model.model_factory.NonLoraModelAndTokenizerFactory import NonLoraModelAndTokenizerFactory
from service.FormalizationService import FormalizationService
from service.ProofSearchService import ProofSearchService

# TODO separate model inference service

app = Flask(__name__)
CORS(app)

device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"Using device: {device}")

print(f"pythia-160M path: {MODEL_PATHS["pythia-160M"]}")

model_short_name_to_config = {
    "pythia-160M":
        NonLoraModelAndPath(
            MODEL_PATHS["pythia-160M"],
            device
        ),
    "pythia-160M-lora":
        LoraModelAndPath(
            MODEL_PATHS["pythia-160M-lora"],
            device
        )
}

# TODO se a dependency injection library?



# TODO check my notes to see what model should be used for formalization
formalization_language_model = FormalizationLanguageModel(
    # "deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B",
    # "deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B",
    "EleutherAI/pythia-160m-deduped",
    device,
    NonLoraModelAndTokenizerFactory()
)

formalization_service = FormalizationService(
    formalization_language_model
)

# proof_search_service = ProofSearchService(language_model, device)
proof_search_service = ProofSearchService(
    formalization_service,
    model_short_name_to_config,
    device
)

proof_search_controller = ProofSearchController(proof_search_service)

logger = EasyLogger()


# TODO status codes and responses should be like in the written thesis

# TODO: send theorem with 'POST'; poll its proof with 'GET'
@app.route('/proof', methods=['GET'])
def proof():
    if request.method == 'GET':
        theorem = request.args.get("theorem") # TODO use body instead of query params (also update written paper)
        model_short_name = request.args.get("model")

        logger.info(f"Received theorem: {theorem}. Requested model: {model_short_name}")

        try:
            generated_proof, successful = proof_search_controller.search_proof(theorem, model_short_name, True)
            logger.info(f"Generated proof (successful: {successful}): {generated_proof}")
            return jsonify({"proof": generated_proof, "successful": successful})
        except ValueError as e:
            return jsonify({"error": str(e)}), 400


@app.route('/proof/informal', methods=['GET'])
def informal_proof():
    if request.method == 'GET':
        theorem = request.args.get("informal_theorem") # TODO use body instead of query params (also update written paper)
        model_short_name = request.args.get("model")

        logger.info(f"Received informal theorem: {theorem}. Requested model: {model_short_name}")

        try:
            generated_proof, successful = proof_search_controller.search_informal_proof(theorem, model_short_name)
            logger.info(f"Generated informal proof (successful: {successful}): {generated_proof}")
            return jsonify({"proof": generated_proof, "successful": successful})
        except ValueError as e:
            return jsonify({"error": str(e)}), 400


@app.route('/proof/fill', methods=['GET'])
def proof_fill():
    if request.method == 'GET':
        theorem_and_partial_proof = request.args.get("theorem_and_partial_proof") # TODO use body instead of query params (also update written paper)
        model_short_name = request.args.get("model")

        logger.info(f"Received theorem and partial proof: {theorem_and_partial_proof}. Requested model: {model_short_name}")

        try:
            generated_proof, successful = proof_search_controller.search_proof(theorem_and_partial_proof, model_short_name, False)
            logger.info(f"Generated proof (successful: {successful}): {generated_proof}")
            return jsonify({"proof": generated_proof, "successful": successful})
        except ValueError as e:
            return jsonify({"error": str(e)}), 400


@app.route('/language_model', methods=['GET', 'PATCH'])
def language_model():
    if request.method == 'GET':
        return jsonify(proof_search_controller.get_language_models())


if __name__ == '__main__':
    app.run()
