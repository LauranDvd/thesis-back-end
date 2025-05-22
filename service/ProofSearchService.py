import sys
from logging import DEBUG

from domain.EasyLogger import EasyLogger
from domain.language_model.ProofSearchLanguageModel import ProofSearchLanguageModel, THEOREM_WAS_PROVED_TACTIC
from domain.language_model.ProofSearchLanguageModel import ERROR_TACTIC


class ProofSearchService:
    def __init__(self, model_short_name_to_config: dict, device):
        self.device = device
        self.model_short_name_to_config = model_short_name_to_config
        self.logger = EasyLogger()


    # theorem should start with "theorem " and end in ":= by"
    def search_proof(self, clean_theorem_statement: str, model_short_name: str) -> (str, bool):
        language_model = self.get_or_load_language_model(model_short_name)

        full_proof = clean_theorem_statement

        for i in range(20):
            next_tactic = language_model.get_next_tactic(full_proof)

            if next_tactic == THEOREM_WAS_PROVED_TACTIC:
                return full_proof, True

            if next_tactic != ERROR_TACTIC:
                full_proof = f"{full_proof}\n{next_tactic}"
                print(f"New full proof after adding a tactic: {full_proof}")
            else:
                self.logger.debug("The tactic resulted in an error; will be ignored")


        return full_proof, False
        # TODO search algorithm


    def get_or_load_language_model(self, model_short_name: str) -> ProofSearchLanguageModel:
        return self.model_short_name_to_config[model_short_name].get_language_model()
        # TODO Get or load

    def get_language_models(self):
        return list(self.model_short_name_to_config.keys())

    def set_language_model(self, language_model: ProofSearchLanguageModel):
        self.language_model = language_model
        self.logger.debug(f"Changed the service's language model")
