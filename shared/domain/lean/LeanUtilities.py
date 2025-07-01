import logging
import re

from domain.EasyLogger import EasyLogger
from domain.lean.ILeanEvaluationInterpreter import ILeanEvaluationInterpreter
from domain.lean.ILeanEvaluator import ILeanEvaluator
from domain.lean.LeanInteractFacade import GOALS_LIST_MESSAGE_PREFIX

MESSAGE_DATA_KEY = "data"

MESSAGES_KEY = "messages"

GOAL_PROOFSTEP_FORMAT = "[GOAL]{}[PROOFSTEP]"

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
        LeanUtilities.logger.debug(f"Formatting program for: {program}")
        repl_output = lean_evaluator.evaluate(program)

        LeanUtilities.logger.debug(f"REPL output: {repl_output}")

        if lean_evaluation_interpreter.is_theorem_solved(repl_output):
            LeanUtilities.logger.debug("The theorem has been proven.")
            return LeanUtilities.PROVED_FORMATTED_PROGRAM

        if lean_evaluation_interpreter.has_errors(repl_output):
            LeanUtilities.logger.debug("REPL output has errors.")
            return LeanUtilities.ERROR_FORMATTED_PROGRAM

        try:
            last_message = repl_output[MESSAGES_KEY][-1] if isinstance(repl_output, dict) else repl_output.messages[-1]
            last_message_data = last_message[MESSAGE_DATA_KEY] if isinstance(last_message,
                                                              dict) else last_message.data
            repl_final_goals = last_message_data[len(GOALS_LIST_MESSAGE_PREFIX):]

            # """[GOAL]m n : ℕ
            #   h : Nat.coprime m n
            #   ⊢ Nat.gcd m n = 1[PROOFSTEP]"""
            return GOAL_PROOFSTEP_FORMAT.format(repl_final_goals)
        except Exception as e:
            LeanUtilities.logger.error(f"Error while building formatted program: {e}")
            return LeanUtilities.ERROR_FORMATTED_PROGRAM

    @staticmethod
    def extract_theorem_statement(theorem: str) -> str:
        match = re.search(r'(theorem .*? by)', theorem)
        return match.group(1) if match else None
