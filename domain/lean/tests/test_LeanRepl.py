from unittest import TestCase

from numpy.ma.testutils import assert_equal

from domain.lean.LeanRepl import LeanRepl


class TestLeanRepl(TestCase):
    def test_repl_output_has_error_messages_returns_true_if_repl_output_has_error_message(self):
        repl_output = {'tactics': [{'usedConstants': [], 'tactic': '<failed to pretty print>', 'proofState': 0,
                                    'pos': {'line': 3, 'column': 0}, 'goals': 'n : ℕ\nh₀ : n ≠ 0\n⊢ 2 ∣ 4 ^ n',
                                    'endPos': {'line': 3, 'column': 5}}], 'messages': [
            {'severity': 'error', 'pos': {'line': 3, 'column': 1}, 'endPos': None, 'data': 'unknown tactic'},
            {'severity': 'error', 'pos': {'line': 2, 'column': 67}, 'endPos': {'line': 3, 'column': 5},
             'data': 'unsolved goals\nn : ℕ\nh₀ : n ≠ 0\n⊢ 2 ∣ 4 ^ n'}], 'env': 0}

        assert_equal(True, LeanRepl.repl_output_has_error_messages(repl_output))

    def test_repl_output_has_error_messages_returns_false_if_repl_output_does_not_have_error_message(self):
        repl_output = {'tactics': [
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

        assert_equal(False, LeanRepl.repl_output_has_error_messages(repl_output))

    def test_does_repl_output_mean_solved_returns_true_if_solved(self):
        repl_output = {'tactics': [{'usedConstants': ['Eq.mpr', 'HMul.hMul', 'congrArg', 'id',
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
        assert_equal(True, LeanRepl.does_repl_output_mean_solved(repl_output))

    def test_does_repl_output_mean_solved_returns_false_if_not_solved(self):
        repl_output = {'tactics': [
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
        assert_equal(False, LeanRepl.does_repl_output_mean_solved(repl_output))
