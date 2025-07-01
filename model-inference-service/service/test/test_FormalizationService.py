from unittest import TestCase
from unittest.mock import MagicMock

from domain.language_model.FormalizationLanguageModel import FormalizationLanguageModel
from domain.lean.ILeanEvaluationInterpreter import ILeanEvaluationInterpreter
from domain.lean.ILeanEvaluator import ILeanEvaluator
from service.FormalizationService import FormalizationService


class TestFormalizationService(TestCase):
    def setUp(self):
        self.lean_evaluator = MagicMock(spec=ILeanEvaluator)
        self.lean_evaluation_interpreter = MagicMock(spec=ILeanEvaluationInterpreter)

        self.formalization_language_model = MagicMock(spec=FormalizationLanguageModel)
        self.formalization_service = FormalizationService(
            self.formalization_language_model
        )

    def test_formalize_returns_formalized_theorem(self):
        expected_formalized_theorem = "formalized theorem"
        self.formalization_language_model.formalize_theorem_statement.return_value = expected_formalized_theorem

        actual_formalized_theorem = self.formalization_service.formalize("informal theorem")
        self.assertEqual(expected_formalized_theorem, actual_formalized_theorem)

    def test_deformalize_returns_deformalized_proof(self):
        expected_informal_proof = "deformalized proof"
        self.formalization_language_model.deformalize_proof.return_value = expected_informal_proof

        actual_informalized_proof = self.formalization_service.deformalize("formal proof")
        self.assertEqual(expected_informal_proof, actual_informalized_proof)

