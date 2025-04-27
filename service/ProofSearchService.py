import sys
from logging import DEBUG

from domain.EasyLogger import EasyLogger
from domain.language_model.IProofSearchLanguageModel import IProofSearchLanguageModel
from domain.language_model.LoraProofSearchLanguageModel import ERROR_TACTIC
from domain.language_model.SimpleProofSearchLanguageModel import SimpleProofSearchLanguageModel, \
    THEOREM_WAS_PROVED_TACTIC


class ProofSearchService:
    def __init__(self, language_model: IProofSearchLanguageModel, device):
        self.device = device
        self.language_model = language_model
        self.logger = EasyLogger.getLogger(DEBUG, sys.stdout)


    # theorem should start with "theorem " and end in ":= by"
    def search_proof(self, clean_theorem_statement: str) -> str:
        full_proof = clean_theorem_statement

        for i in range(20):
            next_tactic = self.language_model.get_next_tactic(full_proof)

            if next_tactic == THEOREM_WAS_PROVED_TACTIC:
                break

            if next_tactic != ERROR_TACTIC:
                full_proof = f"{full_proof}\n{next_tactic}"
                print(f"New full proof after adding a tactic: {full_proof}")
            else:
                self.logger.debug("The tactic resulted in an error; will be ignored")


        return full_proof
        # TODO search algorithm

    def set_language_model(self, language_model: IProofSearchLanguageModel):
        self.language_model = language_model
        self.logger.debug(f"Changed the service's language model")
