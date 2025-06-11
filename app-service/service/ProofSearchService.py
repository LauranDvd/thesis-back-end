import os
import sys
sys.path.append('../')

from domain.EasyLogger import EasyLogger
from domain.language_model.ProofSearchLanguageModel import ProofSearchLanguageModel, THEOREM_WAS_PROVED_TACTIC
from domain.language_model.ProofSearchLanguageModel import ERROR_TACTIC
from service.FormalizationService import FormalizationService


class ProofSearchService:
    def __init__(self, formalization_service: FormalizationService, model_short_name_to_config: dict, device):
        self.__formalization_service = formalization_service
        self.__device = device
        self.__model_short_name_to_config = model_short_name_to_config
        self.__logger = EasyLogger()

    def get_or_load_language_model(self, model_short_name: str) -> ProofSearchLanguageModel:
        return self.__model_short_name_to_config[model_short_name].get_language_model()
        # TODO Get or load

    def get_language_models(self):
        return list(self.__model_short_name_to_config.keys())
