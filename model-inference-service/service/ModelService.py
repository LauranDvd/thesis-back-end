from domain.lean.ILeanEvaluator import ILeanEvaluator

from domain.lean.ILeanEvaluationInterpreter import ILeanEvaluationInterpreter

from domain.language_model.model_configuration.IModelAndPath import IModelAndPath

from domain.language_model.model_configuration.NonLoraModelAndPath import NonLoraModelAndPath
from domain.language_model.model_configuration.LoraModelAndPath import LoraModelAndPath
from domain.EasyLogger import EasyLogger
from repository.TheoremRepository import TheoremRepository
from domain.language_model.model_configuration import LoraModelAndPath


class ModelService:
    def __init__(self, logger: EasyLogger, theorem_repository: TheoremRepository):
        self.__logger = logger
        self.__theorem_repository = theorem_repository

    def get_model_short_name_to_config(
            self,
            device: str,
            lean_evaluator: ILeanEvaluator,
            lean_evaluation_interpreter: ILeanEvaluationInterpreter
    ) -> dict:
        model_short_name_to_config = dict()
        models = self.__theorem_repository.get_language_models()
        for model in models:
            model_and_path: IModelAndPath
            try:
                if model.used_lora:
                    model_and_path = LoraModelAndPath.LoraModelAndPath(
                        model.hf_path,
                        model.base_model_name,
                        device,
                        lean_evaluator,
                        lean_evaluation_interpreter
                    )
                else:
                    model_and_path = NonLoraModelAndPath(
                        model.hf_path,
                        model.base_model_name,
                        device,
                        lean_evaluator,
                        lean_evaluation_interpreter
                    )
                model_short_name_to_config[model.model_name] = model_and_path
            except ValueError as error:
                self.__logger.error(f"Error while loading model {model.model_name}: {error}")

        return model_short_name_to_config
