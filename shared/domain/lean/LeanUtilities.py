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
            lean_evaluation_interpreter: ILeanEvaluationInterpreter
    ) -> str:
        if program[-5:] == "sorry":  # TODO ensure the program gets here without "sorry"
            program = program[:-6]
        program = program.replace("sorry\n", "")
        logging.debug(f"Building formatted program for program: {program}")

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
            last_message = repl_output["messages"][-1] if isinstance(repl_output, dict) else repl_output.messages[-1]
            last_message_data = last_message["data"] if isinstance(last_message,
                                                                   dict) else last_message.data  # TODO remove this workaround
            repl_final_goals = last_message_data[len("unsolved goals\n"):]

            # """[GOAL]m n : ℕ
            #   h : Nat.coprime m n
            #   ⊢ Nat.gcd m n = 1[PROOFSTEP]"""
            return f"[GOAL]{repl_final_goals}[PROOFSTEP]"
        except Exception as e:
            LeanUtilities.logger.error(f"Error while building formatted program: {e}")
            return LeanUtilities.ERROR_FORMATTED_PROGRAM
