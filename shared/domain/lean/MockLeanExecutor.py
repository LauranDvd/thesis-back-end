import random
from typing import override
from unittest.mock import Mock

from shared.domain.EasyLogger import EasyLogger
from shared.domain.lean.ILeanEvaluationInterpreter import ILeanEvaluationInterpreter
from shared.domain.lean.ILeanEvaluator import ILeanEvaluator


class MockLeanExecutor(ILeanEvaluator, ILeanEvaluationInterpreter):
    def __init__(self):
        self.__logger = EasyLogger()

    @override
    def evaluate(self, lean_code: str):
        self.__logger.debug(f"Will mock run this Lean code: {lean_code}")

        last_message = Mock()
        last_message.data = """unsolved goals
x : ℕ
h : x = 2 * 3
⊢ x = 6"""
        lean_output = Mock()
        lean_output.messages = [last_message]

        # repl_final_goals = repl_output.messages[-1].data[len("unsolved goals\n"):]
        self.__logger.debug(f"mock lean server output: {lean_output}")
        return lean_output

    @override
    def is_theorem_solved(self, repl_output) -> bool:
        x = random.randint(0, 4)
        return x == 0

    @override
    def has_errors(self, repl_output) -> bool:
        return False

    @override
    def get_error(self, evaluation_output) -> str:
        return ""

