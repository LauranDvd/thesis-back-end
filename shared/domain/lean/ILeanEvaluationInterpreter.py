class ILeanEvaluationInterpreter:
    def is_theorem_solved(self, evaluation_output) -> bool:
        pass

    def has_errors(self, evaluation_output) -> bool:
        pass

    def get_error(self, evaluation_output) -> str:
        pass
