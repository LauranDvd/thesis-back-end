import os

import torch
from flask import Flask, request, jsonify
from flask_cors import CORS

from config import MODEL_PATHS
from controller.ProofSearchController import ProofSearchController
from domain.EasyLogger import EasyLogger
from domain.language_model.FormalizationLanguageModel import FormalizationLanguageModel
from domain.language_model.model_configuration.NonLoraModelAndPath import NonLoraModelAndPath
from domain.lean.LeanInteractFacade import LeanInteractFacade
from service.FormalizationService import FormalizationService
from service.ProofSearchService import ProofSearchService

# TODO separate model inference service

app = Flask(__name__)
CORS(app)

lean_interact_facade: LeanInteractFacade
proof_search_controller: ProofSearchController
logger: EasyLogger

def initialize():
    global lean_interact_facade, proof_search_controller, logger

    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Using device: {device}")

    lean_interact_facade = LeanInteractFacade()

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
        "pythia-410M-lora":
            NonLoraModelAndPath(
                MODEL_PATHS["pythia-410M-lora"],
                "EleutherAI/pythia-410m-deduped",
                device,
                lean_interact_facade,
                lean_interact_facade
            ),
    }

    # TODO se a dependency injection library?

    # TODO check my notes to see what model should be used for formalization
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

# TODO status codes and responses should be like in the written thesis

# TODO: send theorem with 'POST'; poll its proof with 'GET'
@app.route('/proof', methods=['POST'])
def proof():
    if request.method == 'POST':
        request_data = request.get_json()
        theorem = request_data.get("theorem")
        model_short_name = request_data.get("model")

        logger.info(f"Received theorem: {theorem}. Requested model: {model_short_name}")

        try:
            generated_proof, successful = proof_search_controller.search_proof(theorem, model_short_name, True)
            logger.info(f"Generated proof (successful: {successful}): {generated_proof}")
            return jsonify({"proof": generated_proof, "successful": successful})
        except ValueError as e:
            return jsonify({"error": str(e)}), 400
    return jsonify({"error": "Server error occurred"}), 500


@app.route('/proof/informal', methods=['POST'])
def informal_proof():
    if request.method == 'POST':
        request_data = request.get_json()
        theorem = request_data.get(
            "informal_theorem")
        model_short_name = request_data.get("model")

        logger.info(f"Received informal theorem: {theorem}. Requested model: {model_short_name}")

        try:
            informal_proof_search_result = proof_search_controller.search_informal_proof(theorem, model_short_name)
            logger.info(
                f"Generated informal proof (search success: {informal_proof_search_result.was_search_successful}): {informal_proof_search_result.informal_proof}"
            )

            successful = (
                    informal_proof_search_result.was_formalization_successful and informal_proof_search_result.was_search_successful
                    and informal_proof_search_result.was_deformalization_successful
            )
            return jsonify({
                "proof": informal_proof_search_result.informal_proof,
                "successful": successful,
                "formalized_theorem": informal_proof_search_result.formal_theorem,
                "original_proof": informal_proof_search_result.formal_proof
            })
        except ValueError as e:
            return jsonify({"error": str(e)}), 400
    return jsonify({"error": "Server error occurred"}), 500


@app.route('/proof/fill', methods=['POST'])
def proof_fill():
    if request.method == 'POST':
        request_data = request.get_json()
        theorem_and_partial_proof = request_data.get(
            "theorem_and_partial_proof")
        model_short_name = request_data.get("model")

        logger.info(
            f"Received theorem and partial proof: {theorem_and_partial_proof}. Requested model: {model_short_name}")

        try:
            generated_proof, successful = proof_search_controller.search_proof(theorem_and_partial_proof,
                                                                               model_short_name, False)
            logger.info(f"Generated proof (successful: {successful}): {generated_proof}")
            return jsonify({"proof": generated_proof, "successful": successful})
        except ValueError as e:
            return jsonify({"error": str(e)}), 400
    return jsonify({"error": "Server error occurred"}), 500


@app.route('/language_model', methods=['GET', 'PATCH'])
def language_model():
    if request.method == 'GET':
        return jsonify(proof_search_controller.get_language_models())
    return jsonify({"error": "Server error occurred"}), 500



if __name__ == '__main__':
    app.run()
