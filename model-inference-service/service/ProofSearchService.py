import sys
from logging import DEBUG

from domain.EasyLogger import EasyLogger
from domain.language_model.ProofSearchLanguageModel import ProofSearchLanguageModel, THEOREM_WAS_PROVED_TACTIC
from domain.language_model.ProofSearchLanguageModel import ERROR_TACTIC
from service.FormalizationService import FormalizationService
from service.InformalProofSearchResult import InformalProofSearchResult


class ProofSearchService:
    def __init__(self, formalization_service: FormalizationService, model_short_name_to_config: dict, device):
        self.__formalization_service = formalization_service
        self.__device = device
        self.__model_short_name_to_config = model_short_name_to_config
        self.__logger = EasyLogger()


    # theorem should start with "theorem " and end in ":= by"
    def search_proof(self, clean_theorem_statement: str, model_short_name: str) -> (str, bool):
        language_model = self.get_or_load_language_model(model_short_name)

        full_proof = clean_theorem_statement

        for i in range(10):
            next_tactic = language_model.get_next_tactic(full_proof)

            if next_tactic == THEOREM_WAS_PROVED_TACTIC:
                return full_proof, True

            if next_tactic != ERROR_TACTIC:
                full_proof = f"{full_proof}\n{next_tactic}"
                print(f"New full proof after adding a tactic: {full_proof}")
            else:
                self.__logger.debug("The tactic resulted in an error; will be ignored")

        return full_proof, False
        # TODO search algorithm

    def search_informal_proof(self, informal_statement: str, model_short_name: str) -> InformalProofSearchResult:
        # clean_theorem_statement = """theorem example_theorem (x : Nat) (h : x = 2 * 3) : x + 1 = 7 := by"""
        formal_statement, was_formalization_successful = self.__formalization_service.formalize(informal_statement)
        self.__logger.debug(f"Formalized version of user's informal theorem (successful: {was_formalization_successful}): {formal_statement}")

        if not was_formalization_successful:
            return InformalProofSearchResult(False, False, False, "", "", "") # todo factory methods/builder

        formal_proof, was_proof_search_successful = self.search_proof(formal_statement, model_short_name)
        if not was_proof_search_successful:
            return InformalProofSearchResult(True, False, False, formal_proof, "", formal_statement)

        informal_proof, was_deformalization_successful = self.__formalization_service.deformalize(formal_proof)
        if not was_deformalization_successful:
            return InformalProofSearchResult(True, True, False, formal_proof, informal_proof, formal_statement)
        self.__logger.debug(f"Informalized version of model's formal proof: {informal_proof}")

        return InformalProofSearchResult(True, True, True, formal_proof, informal_proof, formal_statement)


    def get_or_load_language_model(self, model_short_name: str) -> ProofSearchLanguageModel:
        return self.__model_short_name_to_config[model_short_name].get_language_model()
        # TODO Get or load

    def get_language_models(self):
        return list(self.__model_short_name_to_config.keys())

    def set_language_model(self, language_model: ProofSearchLanguageModel):
        self.language_model = language_model
        self.__logger.debug(f"Changed the service's language model")
