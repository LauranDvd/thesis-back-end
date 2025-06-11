from unittest import TestCase
from unittest.mock import patch

from shared.domain.lean.LakeReplFacade import LakeReplFacade
from shared.domain.lean.LeanInteractFacade import LeanInteractFacade
from shared.domain.lean.LeanUtilities import LeanUtilities


class TestLeanUtilities(TestCase):
    def setUp(self):
        self.lean_evaluation_interpreter = LeanInteractFacade()
        self.lean_evaluator = self.lean_evaluation_interpreter

    @patch('domain.lean.LakeReplFacade.LakeReplFacade.evaluate')
    @patch('domain.lean.LakeReplFacade.LakeReplFacade.is_theorem_solved')
    @patch('domain.lean.LakeReplFacade.LakeReplFacade.has_errors')
    def test_build_formatted_program_formats_valid_program_correctly(
            self,
            mock_has_errors,
            mock_is_theorem_solved,
            mock_evaluate
    ):
        mock_has_errors.return_value = False
        mock_is_theorem_solved.return_value = False
        mock_evaluate.return_value = {'tactics': [
            {'usedConstants': [], 'tactic': 'revert n h₀', 'proofState': 1, 'pos': {'line': 3, 'column': 0},
             'goals': 'n : ℕ\nh₀ : n ≠ 0\n⊢ 2 ∣ 4 ^ n', 'endPos': {'line': 3, 'column': 11}},
            {'usedConstants': ['Nat'], 'tactic': 'rintro ⟨k, rfl⟩', 'proofState': 2, 'pos': {'line': 4, 'column': 0},
             'goals': '⊢ ∀ (n : ℕ), n ≠ 0 → 2 ∣ 4 ^ n', 'endPos': {'line': 4, 'column': 15}}, {
                'usedConstants': ['False', 'Dvd.dvd', 'Mathlib.Meta.NormNum.isNat_eq_true', 'eq_false',
                                  'Mathlib.Meta.NormNum.natPow_zero', 'Init.Core._auxLemma.4', 'Nat.instMonoid',
                                  'Monoid.toNatPow', 'not_not_intro', 'Mathlib.Meta.NormNum.isNat_dvd_false', 'Ne',
                                  'instOfNatNat', 'Mathlib.Meta.NormNum.isNat_ofNat', 'Nat.instAddMonoidWithOne',
                                  'Bool.true', 'HPow.hPow', 'Nat.instDvd', 'implies_congr', 'Nat', 'True', 'eq_true',
                                  'Bool.rec', 'Bool', 'of_eq_true', 'Nat.instSemiring', 'Eq.refl', 'instHPow',
                                  'OfNat.ofNat', 'Nat.succ', 'Eq', 'Mathlib.Meta.NormNum.isNat_pow', 'Not', 'Eq.trans',
                                  'True.intro'], 'tactic': 'norm_num', 'proofState': 3, 'pos': {'line': 5, 'column': 2},
                'goals': 'case zero\n⊢ 0 ≠ 0 → 2 ∣ 4 ^ 0', 'endPos': {'line': 5, 'column': 10}},
            {'usedConstants': ['dvd_pow'], 'tactic': 'apply dvd_pow', 'proofState': 4, 'pos': {'line': 6, 'column': 0},
             'goals': 'case succ\nn✝ : ℕ\n⊢ n✝ + 1 ≠ 0 → 2 ∣ 4 ^ (n✝ + 1)', 'endPos': {'line': 6, 'column': 13}}, {
                'usedConstants': ['Dvd.dvd', 'Nat.instMonoid', 'semigroupDvd', 'sorryAx', 'instOfNatNat',
                                  'Lean.Name.num', 'Lean.Name.str', 'Lean.Name.anonymous', 'Nat', 'Monoid.toSemigroup',
                                  'Lean.Name', 'OfNat.ofNat', 'Bool.false'], 'tactic': 'sorry', 'proofState': 5,
                'pos': {'line': 7, 'column': 0}, 'goals': 'case succ.hab\nn✝ : ℕ\n⊢ 2 ∣ 4',
                'endPos': {'line': 7, 'column': 5}}], 'sorries': [
            {'proofState': 0, 'pos': {'line': 7, 'column': 0}, 'goal': 'case succ.hab\nn✝ : ℕ\n⊢ 2 ∣ 4',
             'endPos': {'line': 7, 'column': 5}}], 'messages': [
            {'severity': 'warning', 'pos': {'line': 2, 'column': 8}, 'endPos': {'line': 2, 'column': 30},
             'data': "declaration uses 'sorry'"}], 'env': 0}

        valid_program = """theorem numbertheory_2dvd4expn (n : ℕ) (h₀ : n ≠ 0) : 2 ∣ 4 ^ n := by
  revert n h₀
  rintro ⟨k, rfl⟩
  · norm_num
  apply dvd_pow"""
        expected_formatted_program = """[GOAL]case succ.hab
n✝ : ℕ
⊢ 2 ∣ 4[PROOFSTEP]"""

        self.assertEqual(expected_formatted_program,
                         LeanUtilities.build_formatted_program(valid_program, self.lean_evaluator,
                                                               self.lean_evaluation_interpreter))

    @patch('domain.lean.LakeReplFacade.LakeReplFacade.evaluate')
    @patch('domain.lean.LakeReplFacade.LakeReplFacade.is_theorem_solved')
    @patch('domain.lean.LakeReplFacade.LakeReplFacade.has_errors')
    def test_build_formatted_program_detects_proven_theorem(
            self,
            mock_has_errors,
            mock_is_theorem_solved,
            mock_evaluate
    ):
        mock_has_errors.return_value = False
        mock_is_theorem_solved.return_value = True
        mock_evaluate.return_value = {'tactics': [{'usedConstants': ['Eq.mpr', 'HMul.hMul', 'congrArg', 'id',
                                                                     'instMulNat', 'instOfNatNat', 'instHAdd',
                                                                     'HAdd.hAdd', 'Nat', 'instAddNat', 'OfNat.ofNat',
                                                                     'Eq', 'instHMul'], 'tactic': 'rw [h]',
                                                   'proofState': 0, 'pos': {'line': 3, 'column': 0},
                                                   'goals': 'x : ℕ\nh : x = 2 * 3\n⊢ x + 1 = 7',
                                                   'endPos': {'line': 3, 'column': 6}},
                                                  {'usedConstants': [], 'tactic': 'sorry', 'proofState': 1,
                                                   'pos': {'line': 4, 'column': 0}, 'goals': 'no goals',
                                                   'endPos': {'line': 4, 'column': 5}}], 'messages': [
            {'severity': 'error', 'pos': {'line': 4, 'column': 0}, 'endPos': {'line': 4, 'column': 5},
             'data': 'no goals to be solved'}], 'env': 0}

        valid_program = """theorem my_theorem (x : ℕ) (h : x = 2 * 3) : x + 1 = 7 := by
rw [h]"""

        self.assertEqual(LeanUtilities.PROVED_FORMATTED_PROGRAM,
                         LeanUtilities.build_formatted_program(valid_program, self.lean_evaluator,
                                                               self.lean_evaluation_interpreter))

    @patch('domain.lean.LakeReplFacade.LakeReplFacade.evaluate')
    @patch('domain.lean.LakeReplFacade.LakeReplFacade.is_theorem_solved')
    @patch('domain.lean.LakeReplFacade.LakeReplFacade.has_errors')
    def test_build_formatted_program_returns_error_if_repl_gives_errors(
            self,
            mock_has_errors,
            mock_is_theorem_solved,
            mock_evaluate
    ):
        mock_has_errors.return_value = True
        mock_is_theorem_solved.return_value = False
        mock_evaluate.return_value = {"a": "b"}  # not important

        invalid_program = """theorem numbertheory_2dvd4expn (n : ℕ) (h₀ : n ≠ 0) : 2 ∣ 4 ^ n := by
abcde"""
        self.assertEqual(LeanUtilities.ERROR_FORMATTED_PROGRAM, LeanUtilities.build_formatted_program(invalid_program,
                                                                                                      self.lean_evaluator,
                                                                                                      self.lean_evaluation_interpreter))
