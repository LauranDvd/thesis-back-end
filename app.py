import logging
import sys
import re

from flask import Flask, request, jsonify
import torch
from flask_cors import CORS

from domain.EasyLogger import EasyLogger
from domain.language_model.LoraProofSearchLanguageModel import LoraProofSearchLanguageModel
from domain.language_model.model_configuration.IModelConfiguration import IModelConfiguration
from domain.language_model.SimpleProofSearchLanguageModel import SimpleProofSearchLanguageModel
from domain.language_model.model_configuration.LoraModelConfiguration import LoraModelConfiguration
from domain.language_model.model_configuration.NonLoraModelConfiguration import NonLoraModelConfiguration
from service.ProofSearchService import ProofSearchService

app = Flask(__name__)
CORS(app)

device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"Using device: {device}")

model_short_name_to_config = {
    "pythia-160M":
        NonLoraModelConfiguration(
            "local_resources/language_models/pythia-160M-deduped/checkpoint-2000",
            device
        ),
    "pythia-160M-lora":
        LoraModelConfiguration(
            "local_resources/language_models/id_2_pythia-160M-deduped_lora/checkpoint-2000",
            device
        )
}

# is_model_lora_for_test = False
#
# if is_model_lora_for_test:
#     finetuned_model_path = "local_resources/language_models/id_2_pythia-160M-deduped_lora/checkpoint-2000"
#     language_model = LoraProofSearchLanguageModel(finetuned_model_path, device)
# else:
#     # model_name = "deepseek-ai/DeepSeek-Prover-V1.5-RL"
#     finetuned_model_path = "local_resources/language_models/pythia-160M-deduped/checkpoint-2000"
#     language_model = SimpleProofSearchLanguageModel(finetuned_model_path, device)

language_model_short_name = "pythia-160M"

# proof_search_service = ProofSearchService(language_model, device)
proof_search_service = ProofSearchService(
    model_short_name_to_config[language_model_short_name].get_language_model(),
    device
)

logger = EasyLogger.getLogger(logging.DEBUG, sys.stdout)


def extract_theorem_statement(theorem: str) -> str:
    match = re.search(r'(theorem .*? by)', theorem)
    return match.group(1) if match else None


@app.route('/proof', methods=['GET'])
def proof():
    if request.method == 'GET':
        theorem = request.args.get("theorem")
        if not theorem:
            return jsonify({"error": "No theorem provided"}), 400

        logger.info(f"Received theorem: {theorem}")

        theorem_statement = extract_theorem_statement(theorem)
        logger.info(f"Clean theorem statement: {theorem_statement}")

        generated_proof = proof_search_service.search_proof(theorem_statement)

        logger.info(f"Generated proof: {generated_proof}")

        return jsonify({"proof": generated_proof})


@app.route('/proof/fill', methods=['GET'])
def proof_fill():
    if request.method == 'GET':
        theorem_and_partial_proof = request.args.get("theorem_and_partial_proof")
        if not theorem_and_partial_proof:
            return jsonify({"error": "No theorem and partial proof provided"}), 400

        logger.info(f"Received theorem and partial proof: {theorem_and_partial_proof}")

        # theorem_statement = extract_theorem_statement(theorem)
        # logger.info(f"Clean theorem statement: {theorem_statement}")

        generated_proof = proof_search_service.search_proof(theorem_and_partial_proof)

        logger.info(f"Generated proof: {generated_proof}")

        return jsonify({"proof": generated_proof})


@app.route('/language_model', methods=['GET', 'PATCH'])
def language_model():
    if request.method == 'GET':
        return jsonify({
            "current": language_model_short_name,
            "all": list(model_short_name_to_config.keys())
        })
    if request.method == 'PATCH':
        model_name = request.get_json().get("model_name")
        if not model_name:
            return jsonify({"error": "No model name provided"}), 400

        supported_models = model_short_name_to_config.keys()
        if model_name not in supported_models:
            return jsonify({"error": f"Model {model_name} not supported. Supported models: {supported_models}"}), 400

        logger.info(f"Setting language model to {model_name}")
        proof_search_service.set_language_model(model_short_name_to_config[model_name].get_language_model())
        return jsonify({"success": True})

if __name__ == '__main__':
    app.run()
