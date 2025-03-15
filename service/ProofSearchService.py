from domain.language_model.ProofSearchLanguageModel import ProofSearchLanguageModel


class ProofSearchService:
    def __init__(self, model_name, device):
        self.model_name = model_name  # TODO use my fine-tuned model
        self.device = device
        self.language_model = ProofSearchLanguageModel(self.model_name, self.device)


    def search_proof(self, theorem: str) -> str:
        output_proof = self.language_model.get_next_tactic(theorem)
        return output_proof
        # TODO search algorithm


