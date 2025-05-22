import logging
import sys

from domain.EasyLogger import EasyLogger
from domain.lean.ILeanEvaluationInterpreter import ILeanEvaluationInterpreter
from domain.lean.ILeanEvaluator import ILeanEvaluator


class LeanUtilities:
    PROVED_FORMATTED_PROGRAM = f"[GOAL]no goals[PROOFSTEP]"
    ERROR_FORMATTED_PROGRAM = "error"

    logger = EasyLogger()

    @staticmethod
    def build_formatted_program(
            program: str,
            lean_evaluator: ILeanEvaluator,
            lean_evaluation_interpreter: ILeanEvaluationInterpreter,
            add_mathlib_import=True
    ) -> str:
        if program[-5:] == "sorry":  # TODO ensure the program gets here without "sorry"
            program = program[:-6]
        program = program.replace("sorry\n", "")
        logging.debug(f"Building formatted program for program: {program}")

        if add_mathlib_import:
            program = f"import Mathlib\n{program}"
        program = f"{program}\nsorry"

        LeanUtilities.logger.debug(f"Formatting program for: {program}")
        repl_output = lean_evaluator.evaluate(program)

        print(f"repl output: {repl_output}")

        if lean_evaluation_interpreter.is_theorem_solved(repl_output):
            LeanUtilities.logger.debug("The theorem has been proven.")
            return LeanUtilities.PROVED_FORMATTED_PROGRAM

        if lean_evaluation_interpreter.has_errors(repl_output):
            LeanUtilities.logger.debug("REPL output has errors.")
            return LeanUtilities.ERROR_FORMATTED_PROGRAM

        try:
            repl_tactics = repl_output["tactics"]
            repl_last_tactic = repl_tactics[-1]
            repl_final_goals = repl_last_tactic["goals"]

            # """[GOAL]m n : ℕ
            #   h : Nat.coprime m n
            #   ⊢ Nat.gcd m n = 1[PROOFSTEP]"""
            return f"[GOAL]{repl_final_goals}[PROOFSTEP]"
        except Exception as e:
            LeanUtilities.logger.error(f"Error while building formatted program: {e}")
            return LeanUtilities.ERROR_FORMATTED_PROGRAM
