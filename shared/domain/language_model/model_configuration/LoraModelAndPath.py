from typing_extensions import override

from domain.language_model.ProofSearchLanguageModel import ProofSearchLanguageModel
from domain.language_model.model_configuration.IModelAndPath import IModelAndPath
from domain.language_model.model_factory.LoraModelAndTokenizerFactory import LoraModelAndTokenizerFactory
from domain.lean.ILeanEvaluationInterpreter import ILeanEvaluationInterpreter
from domain.lean.ILeanEvaluator import ILeanEvaluator


class LoraModelAndPath(IModelAndPath):
    def __init__(self, model_path: str, base_model_name: str, device: str,
                 lean_evaluator: ILeanEvaluator,
                 lean_evaluation_interpreter: ILeanEvaluationInterpreter):
        self.__model_path = model_path
        self.__language_model = ProofSearchLanguageModel(
            model_path, base_model_name, device, LoraModelAndTokenizerFactory(),
            lean_evaluator, lean_evaluation_interpreter
        )

    @override
    def get_model_path(self) -> str:
        return self.__model_path

    @override
    def get_language_model(self) -> ProofSearchLanguageModel:
        return self.__language_model
