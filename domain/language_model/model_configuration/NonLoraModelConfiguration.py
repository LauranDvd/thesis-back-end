from typing import override

from domain.language_model.IProofSearchLanguageModel import IProofSearchLanguageModel
from domain.language_model.SimpleProofSearchLanguageModel import SimpleProofSearchLanguageModel
from domain.language_model.model_configuration.IModelConfiguration import IModelConfiguration

# TODO this class is not good: the LM is not a config thing, and it's not on same level as model_path
class NonLoraModelConfiguration(IModelConfiguration):
    def __init__(self, model_path: str, device: str):
        self.model_path = model_path
        self.language_model = SimpleProofSearchLanguageModel(model_path, device)

    @override
    def get_model_path(self) -> str:
        return self.model_path

    @override
    def get_language_model(self) -> IProofSearchLanguageModel:
        return self.language_model
