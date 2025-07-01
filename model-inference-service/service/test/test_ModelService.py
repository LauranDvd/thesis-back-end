from unittest import TestCase
from unittest.mock import MagicMock, patch

from domain.EasyLogger import EasyLogger
from domain.lean.ILeanEvaluationInterpreter import ILeanEvaluationInterpreter
from domain.lean.ILeanEvaluator import ILeanEvaluator
from repository.TheoremRepository import TheoremRepository
from repository.orm.Entities import LanguageModelEntity
from service.ModelService import ModelService


class TestModelService(TestCase):
    def setUp(self):
        self.models = [
            LanguageModelEntity(model_id=1, model_name="first_name", base_model_name="first_name", used_lora=False,
                                hf_path="http"),
            LanguageModelEntity(model_id=2, model_name="second_name", base_model_name="second_name", used_lora=True,
                                hf_path="http2"),
        ]
        self.theorem_repository = MagicMock(spec=TheoremRepository)
        self.theorem_repository.get_language_models.return_value = self.models

        self.model_service = ModelService(
            EasyLogger(),
            self.theorem_repository
        )

    @patch("domain.language_model.model_configuration.NonLoraModelAndPath.NonLoraModelAndPath.__init__")
    @patch("domain.language_model.model_configuration.LoraModelAndPath.LoraModelAndPath.__init__")
    def test_get_model_short_name_to_config_returns_models(
            self,
            mock_lora_init,
            mock_non_lora_init
    ):
        mock_lora_init.return_value = None
        mock_non_lora_init.return_value = None

        mock_lean_evaluator = MagicMock(spec=ILeanEvaluator)
        mock_lean_evaluation_interpreter = MagicMock(spec=ILeanEvaluationInterpreter)

        actual_config = self.model_service.get_model_short_name_to_config("cpu", mock_lean_evaluator,
                                                                          mock_lean_evaluation_interpreter)
        self.assertEqual(len(self.models), len(actual_config))
