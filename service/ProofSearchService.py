from domain.language_model.SimpleProofSearchLanguageModel import SimpleProofSearchLanguageModel


class ProofSearchService:
    def __init__(self, language_model, device):
        self.device = device
        self.language_model = language_model


    # theorem should start with "theorem " and end in ":= by"
    def search_proof(self, clean_theorem_statement: str) -> str:
        full_proof = clean_theorem_statement

        for i in range(8):
            next_tactic = self.language_model.get_next_tactic(clean_theorem_statement)
            full_proof = f"{full_proof}\n{next_tactic}"

        return full_proof
        # TODO search algorithm


