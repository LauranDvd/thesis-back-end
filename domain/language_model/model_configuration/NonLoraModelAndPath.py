from typing import override

from domain.language_model.ProofSearchLanguageModel import ProofSearchLanguageModel
from domain.language_model.model_configuration.IModelAndPath import IModelAndPath
from domain.language_model.model_factory.NonLoraModelAndTokenizerFactory import NonLoraModelAndTokenizerFactory


class NonLoraModelAndPath(IModelAndPath):
    def __init__(self, model_path: str, device: str):
        self.model_path = model_path
        self.language_model = ProofSearchLanguageModel(model_path, device, NonLoraModelAndTokenizerFactory())

    @override
    def get_model_path(self) -> str:
        return self.model_path

    @override
    def get_language_model(self) -> ProofSearchLanguageModel:
        return self.language_model
