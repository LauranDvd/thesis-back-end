from typing_extensions import override

from domain.language_model.IProofSearchLanguageModel import IProofSearchLanguageModel
from domain.language_model.LoraProofSearchLanguageModel import LoraProofSearchLanguageModel
from domain.language_model.model_configuration.IModelConfiguration import IModelConfiguration


class LoraModelConfiguration(IModelConfiguration):
    def __init__(self, model_path: str, device: str):
        self.model_path = model_path
        self.language_model = LoraProofSearchLanguageModel(model_path, device)

    @override
    def get_model_path(self) -> str:
        return self.model_path

    @override
    def get_language_model(self) -> IProofSearchLanguageModel:
        return self.language_model
