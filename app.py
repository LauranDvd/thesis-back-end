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

# proof_search_service = ProofSearchService(language_model, device)
proof_search_service = ProofSearchService(
    model_short_name_to_config,
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
        model_short_name = request.args.get("model")
        if not model_short_name:
            return jsonify({"error": "No language model name provided"}), 400

        logger.info(f"Received theorem: {theorem}. Requested model: {model_short_name}")

        theorem_statement = extract_theorem_statement(theorem)
        logger.info(f"Clean theorem statement: {theorem_statement}")

        generated_proof, successful = proof_search_service.search_proof(theorem_statement, model_short_name)

        logger.info(f"Generated proof (successful: {successful}): {generated_proof}")

        return jsonify({"proof": generated_proof, "successful": successful})


@app.route('/proof/fill', methods=['GET'])
def proof_fill():
    if request.method == 'GET':
        theorem_and_partial_proof = request.args.get("theorem_and_partial_proof")
        if not theorem_and_partial_proof:
            return jsonify({"error": "No theorem and partial proof provided"}), 400

        logger.info(f"Received theorem and partial proof: {theorem_and_partial_proof}")

        # theorem_statement = extract_theorem_statement(theorem)
        # logger.info(f"Clean theorem statement: {theorem_statement}")

        generated_proof, successful = proof_search_service.search_proof(theorem_and_partial_proof)

        logger.info(f"Generated proof (succesful: {successful}): {generated_proof}")

        return jsonify({"proof": generated_proof, "successful": successful})


@app.route('/language_model', methods=['GET', 'PATCH'])
def language_model():
    if request.method == 'GET':
        return jsonify(list(model_short_name_to_config.keys()))


if __name__ == '__main__':
    app.run()
