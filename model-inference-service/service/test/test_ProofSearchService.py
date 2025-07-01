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
    def test_search_proof_returns_proof_and_true_if_already_proven(
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
    @patch("domain.lean.LeanUtilities.LeanUtilities.build_formatted_program")
    def test_search_proof_returns_proof_and_true_if_proven(
            self,
            mock_build_formatted_program,
            mock_get_or_load_language_model
    ):
        mock_build_formatted_program.side_effect = ["[GOAL]a[PROOFSTEP]b", LeanUtilities.PROVED_FORMATTED_PROGRAM]

        returned_tactic = "abc"

        mock_proof_search_language_model = MagicMock(spec=ProofSearchLanguageModel)
        mock_proof_search_language_model.get_several_next_tactics.return_value = [returned_tactic], [1.1]
        mock_get_or_load_language_model.return_value = mock_proof_search_language_model

        theorem = """import Mathlib

theorem my_theorem (x : Nat) (h : x = 2 * 3) : x + 1 = 7 := by"""

        proof, is_proof_found = self.proof_search_service.search_proof(theorem, "model1")
        self.assertTrue(is_proof_found)
        self.assertEqual(theorem + "\n" + returned_tactic, proof)

    @patch("service.ProofSearchService.ProofSearchService.get_or_load_language_model")
    @patch("domain.lean.LeanUtilities.LeanUtilities.build_formatted_program")
    def test_search_proof_returns_partial_proof_and_false_if_proof_not_found(
            self,
            mock_build_formatted_program,
            mock_get_or_load_language_model
    ):
        mock_build_formatted_program.side_effect = [f"[GOAL]{random_part}[PROOFSTEP]{random_part}" for random_part in
                                                    range(ProofSearchService.SEARCH_BUDGET)]

        mock_proof_search_language_model = MagicMock(spec=ProofSearchLanguageModel)
        mock_tactic = "mock_tactic"
        mock_proof_search_language_model.get_several_next_tactics.return_value = [mock_tactic], [1.1]
        mock_get_or_load_language_model.return_value = mock_proof_search_language_model

        theorem = """import Mathlib

theorem my_theorem (x : Nat) (h : x = 2 * 3) : x + 1 = 7 := by
linarith"""

        proof, is_proof_found = self.proof_search_service.search_proof(theorem, "model1")
        self.assertFalse(is_proof_found)
        count_tactics = ProofSearchService.SEARCH_BUDGET // ProofSearchService.SEARCH_BUDGET_PER_STEP
        if ProofSearchService.SEARCH_BUDGET % ProofSearchService.SEARCH_BUDGET_PER_STEP:
            count_tactics += 1
        self.assertEqual(theorem + ("\n" + mock_tactic) * count_tactics, proof)


    @patch("service.ProofSearchService.ProofSearchService.get_or_load_language_model")
    @patch("domain.lean.LeanUtilities.LeanUtilities.build_formatted_program")
    def test_search_informal_proof_returns_proof_and_true_if_proven(
            self,
            mock_build_formatted_program,
            mock_get_or_load_language_model
    ):
        mock_build_formatted_program.side_effect = ["[GOAL]a[PROOFSTEP]b", LeanUtilities.PROVED_FORMATTED_PROGRAM]
        self.formalization_service.formalize.return_value = """import Mathlib

theorem my_theorem (x : Nat) (h : x = 2 * 3) : x + 1 = 7 := by""", True
        expected_informal_proof = "this is the informal proof"
        self.formalization_service.deformalize.return_value = "this is the informal proof", True

        returned_tactic = "abc"

        expected_formal_proof = self.formalization_service.formalize.return_value[0] + "\n" + returned_tactic

        mock_proof_search_language_model = MagicMock(spec=ProofSearchLanguageModel)
        mock_proof_search_language_model.get_several_next_tactics.return_value = [returned_tactic], [1.1]
        mock_get_or_load_language_model.return_value = mock_proof_search_language_model

        informal_proof_search_result = self.proof_search_service.search_informal_proof("informal statement", "model1")
        self.assertTrue(informal_proof_search_result.was_search_successful)
        self.assertEqual(expected_informal_proof, informal_proof_search_result.informal_proof)
        self.assertEqual(expected_formal_proof, informal_proof_search_result.formal_proof)


    @patch("domain.lean.LeanUtilities.LeanUtilities.build_formatted_program")
    def test_search_informal_proof_returns_formalization_unsuccessful_if_so(
            self,
            mock_build_formatted_program
    ):
        mock_build_formatted_program.side_effect = ["[GOAL]a[PROOFSTEP]b", LeanUtilities.PROVED_FORMATTED_PROGRAM]
        self.formalization_service.formalize.return_value = "", False

        informal_proof_search_result = self.proof_search_service.search_informal_proof("informal statement", "model1")
        self.assertFalse(informal_proof_search_result.was_formalization_successful)
