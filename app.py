import logging
import sys
import re

from flask import Flask, request, jsonify
import torch
from flask_cors import CORS

from domain.EasyLogger import EasyLogger
from domain.language_model.LoraProofSearchLanguageModel import LoraProofSearchLanguageModel
from domain.language_model.SimpleProofSearchLanguageModel import SimpleProofSearchLanguageModel
from service.ProofSearchService import ProofSearchService

app = Flask(__name__)
CORS(app)

device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"Using device: {device}")

is_model_lora_for_test = False

if is_model_lora_for_test:
    finetuned_model_path = "local_resources/language_models/id_2_pythia-160M-deduped_lora/checkpoint-2000"
    language_model = LoraProofSearchLanguageModel(finetuned_model_path, device)
else:
    # model_name = "deepseek-ai/DeepSeek-Prover-V1.5-RL"
    finetuned_model_path = "local_resources/language_models/pythia-160M-deduped/checkpoint-2000"
    language_model = SimpleProofSearchLanguageModel(finetuned_model_path, device)

proof_search_service = ProofSearchService(language_model, device)

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


if __name__ == '__main__':
    app.run()
