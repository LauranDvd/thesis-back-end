from unittest import TestCase
from unittest.mock import patch, MagicMock

from domain.language_model.ProofSearchLanguageModel import ProofSearchLanguageModel, THEOREM_WAS_PROVED_TACTIC
from domain.language_model.model_configuration.NonLoraModelAndPath import NonLoraModelAndPath
from domain.lean.ILeanEvaluationInterpreter import ILeanEvaluationInterpreter
from domain.lean.ILeanEvaluator import ILeanEvaluator
from domain.lean.LeanUtilities import LeanUtilities
from service.FormalizationService import FormalizationService
from service.ProofSearchService import ProofSearchService


class TestProofSearchService(TestCase):
    def setUp(self):
        self.model_and_path = MagicMock(spec=NonLoraModelAndPath)
        self.formalization_service = MagicMock(spec=FormalizationService)
        self.lean_evaluator = MagicMock(spec=ILeanEvaluator)
        self.lean_evaluation_interpreter = MagicMock(spec=ILeanEvaluationInterpreter)
        self.proof_search_service = ProofSearchService(
            self.formalization_service,
            self.lean_evaluator,
            self.lean_evaluation_interpreter,
            {"model1": self.model_and_path},
            "cpu"
        )

    @patch("service.ProofSearchService.ProofSearchService.get_or_load_language_model")
    @patch("domain.lean.LeanUtilities.LeanUtilities.build_formatted_program")
    def test_search_proof_returns_proof_and_true_if_proof_found(
            self,
            mock_build_formatted_program,
            mock_get_or_load_language_model
    ):
        mock_build_formatted_program.return_value = LeanUtilities.PROVED_FORMATTED_PROGRAM

        mock_proof_search_language_model = MagicMock(spec=ProofSearchLanguageModel)
        mock_proof_search_language_model.get_several_next_tactics.return_value = ["abc"], [1.1]
        mock_get_or_load_language_model.return_value = mock_proof_search_language_model

        theorem = """import Mathlib

theorem my_theorem (x : Nat) (h : x = 2 * 3) : x + 1 = 7 := by
linarith"""

        proof, is_proof_found = self.proof_search_service.search_proof(theorem, "model1")
        self.assertTrue(is_proof_found)
        self.assertEqual(theorem, proof)

    @patch("service.ProofSearchService.ProofSearchService.get_or_load_language_model")
    def test_search_proof_returns_partial_proof_and_false_if_proof_not_found(
            self,
            mock_get_or_load_language_model
    ):
        mock_proof_search_language_model = MagicMock(spec=ProofSearchLanguageModel)
        mock_tactic = "mock_tactic"
        mock_proof_search_language_model.get_next_tactic.return_value = mock_tactic
        mock_get_or_load_language_model.return_value = mock_proof_search_language_model

        theorem = """import Mathlib

theorem my_theorem (x : Nat) (h : x = 2 * 3) : x + 1 = 7 := by
linarith"""

        proof, is_proof_found = self.proof_search_service.search_proof(theorem, "model1")
        self.assertFalse(is_proof_found)
        self.assertEqual(theorem + ("\n" + mock_tactic) * 10, proof)
