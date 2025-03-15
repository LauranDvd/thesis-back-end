from flask import Flask, request, jsonify
import torch

from service.ProofSearchService import ProofSearchService

app = Flask(__name__)

model_name = "Maykeye/TinyLLama-v0"
device = "cuda" if torch.cuda.is_available() else "cpu"

proof_search_service = ProofSearchService(model_name, device)

@app.route('/proof', methods=['GET'])
def proof():
    theorem = request.args.get("theorem")
    if not theorem:
        return jsonify({"error": "No theorem provided"}), 400

    generated_proof = proof_search_service.search_proof(theorem)
    return jsonify({"proof": generated_proof})


if __name__ == '__main__':
    app.run()
