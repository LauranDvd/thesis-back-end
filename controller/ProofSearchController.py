import sys
from logging import DEBUG
import re

from domain.EasyLogger import EasyLogger
from service.ProofSearchService import ProofSearchService


class ProofSearchController:
    def __init__(self, proof_search_service: ProofSearchService):
        self.proof_search_service = proof_search_service
        self.logger = EasyLogger()

    def search_proof(self, theorem: str, model_short_name: str, should_clean_the_theorem: bool):
        if not theorem:
            raise ValueError("No theorem provided")
        if not model_short_name:
            raise ValueError("No language model name provided")

        if should_clean_the_theorem:
            theorem = self.__extract_theorem_statement(theorem)
            self.logger.info(f"Clean theorem statement: {theorem}")

        return self.proof_search_service.search_proof(theorem, model_short_name)

    def search_informal_proof(self, theorem: str, model_short_name: str):
        if not theorem:
            raise ValueError("No theorem provided")
        if not model_short_name:
            raise ValueError("No language model name provided")
        return self.proof_search_service.search_informal_proof(theorem, model_short_name)

    def get_language_models(self):
        return self.proof_search_service.get_language_models()

    @staticmethod
    def __extract_theorem_statement(theorem: str) -> str:
        match = re.search(r'(theorem .*? by)', theorem)
        return match.group(1) if match else None
