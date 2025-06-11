from typing import override

from shared.domain.language_model.ProofSearchLanguageModel import ProofSearchLanguageModel
from shared.domain.language_model.model_configuration.IModelAndPath import IModelAndPath
from shared.domain.language_model.model_factory.NonLoraModelAndTokenizerFactory import NonLoraModelAndTokenizerFactory
from shared.domain.lean.ILeanEvaluationInterpreter import ILeanEvaluationInterpreter
from shared.domain.lean.ILeanEvaluator import ILeanEvaluator

class NonLoraModelAndPath(IModelAndPath):
    def __init__(
            self, model_path: str, base_model_name: str, device: str,
            lean_evaluator: ILeanEvaluator,
            lean_evaluation_interpreter: ILeanEvaluationInterpreter
    ):
        self.__model_path = model_path
        self.__language_model = ProofSearchLanguageModel(
            model_path, base_model_name, device, NonLoraModelAndTokenizerFactory(),
            lean_evaluator, lean_evaluation_interpreter
        )

    @override
    def get_model_path(self) -> str:
        return self.__model_path

    @override
    def get_language_model(self) -> ProofSearchLanguageModel:
        return self.__language_model
