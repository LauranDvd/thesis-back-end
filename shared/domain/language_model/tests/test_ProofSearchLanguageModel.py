from unittest import TestCase
from unittest.mock import patch, MagicMock

from domain.language_model.ProofSearchLanguageModel import ProofSearchLanguageModel, THEOREM_WAS_PROVED_TACTIC, \
    ERROR_TACTIC
from domain.language_model.model_factory.NonLoraModelAndTokenizerFactory import NonLoraModelAndTokenizerFactory
from domain.lean.ILeanEvaluationInterpreter import ILeanEvaluationInterpreter
from domain.lean.ILeanEvaluator import ILeanEvaluator
from domain.lean.LeanUtilities import LeanUtilities


class TestProofSearchLanguageModel(TestCase):
    def setUp(self):
        self.finetuned_model_path = "fake_path"
        # self.model_and_tokenizer_factory = NonLoraModelAndTokenizerFactory()
        self.model_and_tokenizer_factory = MagicMock(spec=NonLoraModelAndTokenizerFactory)
        self.mock_model = MagicMock()
        self.mock_model.generate.return_value = ["tactic 1", "tactic 2"]
        self.model_and_tokenizer_factory.get_model.return_value = self.mock_model
        self.lean_evaluator = MagicMock(spec=ILeanEvaluator)
        self.lean_evaluation_interpreter = MagicMock(spec=ILeanEvaluationInterpreter)

        self.proof_search_language_model = ProofSearchLanguageModel(self.finetuned_model_path, "base_model",
                                                                    "cpu",
                                                                    self.model_and_tokenizer_factory,
                                                                    self.lean_evaluator,
                                                                    self.lean_evaluation_interpreter
                                                                    )


    def test_get_next_tactic_returns_theorem_was_proved_if_theorem_is_already_proved(
            self
    ):
        theorem = """import Mathlib

theorem my_theorem (x : Nat) (h : x = 2 * 3) : x + 1 = 7 := by
linarith
"""
        expected_next_tactic = THEOREM_WAS_PROVED_TACTIC
        actual_next_tactic = self.proof_search_language_model.get_next_tactic(theorem)
        self.assertEqual(expected_next_tactic, actual_next_tactic)

    @patch("domain.lean.LeanUtilities.LeanUtilities.build_formatted_program",
           return_value=LeanUtilities.ERROR_FORMATTED_PROGRAM)
    def test_get_next_tactic_returns_error_tactic_if_model_proposes_invalid_tactic(
            self,
            mock_build_formatted_program
    ):
        mock_build_formatted_program.return_value = LeanUtilities.ERROR_FORMATTED_PROGRAM
        theorem = """import Mathlib

theorem my_theorem (x : Nat) (h : x = 2 * 3) : x + 1 = 7 := by
linarith
"""
        expected_next_tactic = ERROR_TACTIC
        actual_next_tactic = self.proof_search_language_model.get_next_tactic(theorem)
        self.assertEqual(expected_next_tactic, actual_next_tactic)

    @patch("domain.lean.LeanUtilities.LeanUtilities.build_formatted_program",
           return_value="abcd")
    def test_get_next_tactic_returns_tactic_if_valid_and_theorem_not_proven_yet(
            self,
            mock_build_formatted_program
    ):
        mock_build_formatted_program.return_value = "mock_tactic"

        theorem = """import Mathlib

theorem my_theorem (x : Nat) (h : x = 2 * 3) : x + 1 = 7 := by
sorry
"""
        actual_next_tactic = self.proof_search_language_model.get_next_tactic(theorem)
        self.assertNotEqual(THEOREM_WAS_PROVED_TACTIC, actual_next_tactic)
        self.assertNotEqual(ERROR_TACTIC, actual_next_tactic)
