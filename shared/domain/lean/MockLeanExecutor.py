import random
from typing import override
from unittest.mock import Mock

from domain.EasyLogger import EasyLogger
from domain.lean.ILeanEvaluationInterpreter import ILeanEvaluationInterpreter
from domain.lean.ILeanEvaluator import ILeanEvaluator

# MockLeanExecutor will say that this contains errors
THEOREM_AND_PARTIAL_PROOF_WITH_ERRORS = """theorem test_theorem (x : Nat) (h : x = 2 * 3) : x + 1 = 7 := by
fgdhgtfd"""
MOCK_LEAN_ERROR = "Mock lean error"

class MockLeanExecutor(ILeanEvaluator, ILeanEvaluationInterpreter):
    MOCK_GOALS = [
        """unsolved goals
x : ℕ
h : x = 2 * 3
⊢ x + 1 = 7""",
        """unsolved goals
x : ℕ
h : x = 2 * 3
⊢ x = 6""",
        """unsolved goals
x : ℕ
h : x + 1 = 5
⊢ x = 4"""
    ]

    def __init__(self):
        self.__logger = EasyLogger()

    @override
    def evaluate(self, lean_code: str):
        self.__logger.debug(f"Will mock run this Lean code: {lean_code}")

        last_message = Mock()
        if lean_code == THEOREM_AND_PARTIAL_PROOF_WITH_ERRORS:
            last_message.data = MOCK_LEAN_ERROR
        else:
            last_message.data = MockLeanExecutor.MOCK_GOALS[random.randint(0, len(MockLeanExecutor.MOCK_GOALS) - 1)]
        lean_output = Mock()
        lean_output.messages = [last_message]

        # repl_final_goals = repl_output.messages[-1].data[len("unsolved goals\n"):]
        self.__logger.debug(f"mock lean server output: {lean_output}")
        return lean_output

    @override
    def is_theorem_solved(self, repl_output) -> bool:
        x = random.randint(0, 3)
        return x == 0

    @override
    def has_errors(self, repl_output) -> bool:
        if repl_output.messages[-1].data == MOCK_LEAN_ERROR:
            return True
        return False

    @override
    def get_error(self, evaluation_output) -> str:
        if evaluation_output.messages[-1].data == MOCK_LEAN_ERROR:
            return MOCK_LEAN_ERROR
        return ""
