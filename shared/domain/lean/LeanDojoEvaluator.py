from typing import override

from domain.lean.ILeanEvaluator import ILeanEvaluator


class LeanDojoEvaluator(ILeanEvaluator):
    @override
    def evaluate(self, lean_code: str) -> dict:
        pass
