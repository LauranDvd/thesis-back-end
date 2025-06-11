from typing import override

from shared.domain.lean.ILeanEvaluator import ILeanEvaluator


class LeanDojoEvaluator(ILeanEvaluator):
    @override
    def evaluate(self, lean_code: str) -> dict:
        pass
