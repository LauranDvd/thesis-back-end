from unittest import TestCase
from unittest.mock import patch, MagicMock

from domain.language_model.ProofSearchLanguageModel import ProofSearchLanguageModel, THEOREM_WAS_PROVED_TACTIC
from domain.language_model.model_configuration.NonLoraModelAndPath import NonLoraModelAndPath
from service.ProofSearchService import ProofSearchService


class TestProofSearchService(TestCase):
    def setUp(self):
        self.model_and_path = MagicMock(spec=NonLoraModelAndPath)
        self.proof_search_service = ProofSearchService({"model1": self.model_and_path}, "cpu")

    @patch("service.ProofSearchService.ProofSearchService.get_or_load_language_model")
    def test_search_proof_returns_proof_and_true_if_proof_found(
            self,
            mock_get_or_load_language_model
    ):
        mock_proof_search_language_model = MagicMock(spec=ProofSearchLanguageModel)
        mock_proof_search_language_model.get_next_tactic.return_value = THEOREM_WAS_PROVED_TACTIC
        mock_get_or_load_language_model.return_value = mock_proof_search_language_model

        theorem = """import Mathlib

theorem my_theorem (x : Nat) (h : x = 2 * 3) : x + 1 = 7 := by
linarith"""

        proof, is_proof_found = ProofSearchService.search_proof(self.proof_search_service, theorem, "model1")
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

        proof, is_proof_found = ProofSearchService.search_proof(self.proof_search_service, theorem, "model1")
        self.assertFalse(is_proof_found)
        self.assertEqual(theorem + ("\n" + mock_tactic) * 20, proof) # TODO search budget instead of 20
