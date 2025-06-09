import json
from typing import override

from lean_interact import LeanREPLConfig, TempRequireProject, AutoLeanServer, LeanServer, Command
from lean_interact.interface import LeanError

from domain.EasyLogger import EasyLogger
from domain.lean.ILeanEvaluationInterpreter import ILeanEvaluationInterpreter
from domain.lean.ILeanEvaluator import ILeanEvaluator


class LeanInteractFacade(ILeanEvaluator, ILeanEvaluationInterpreter):
    MAXIMUM_RUN_ATTEMPTS = 3

    def __init__(self):
        self.logger = EasyLogger()
        self.__initialize_lean_environment()

    @override
    def evaluate(self, lean_code: str):
        self.logger.debug(f"Will run this Lean code: {lean_code}")

        ran_successfully = False
        run_attempts = 0
        lean_output = None
        while not ran_successfully and run_attempts < LeanInteractFacade.MAXIMUM_RUN_ATTEMPTS:
            self.logger.debug(f"Will run code on the lean server")
            lean_output = self.lean_server.run(Command(cmd=lean_code, all_tactics=True, env=self.env_number))
            self.logger.debug(f"Finished running code on the lean server")
            if type(lean_output) is LeanError:
                if lean_output.message == "Unknown environment.": # todo add constants
                    self.logger.debug("The Lean executor does not recognize the environment. Will reinitialize the environment.")
                    self.__initialize_lean_environment()
            else:
                ran_successfully = True
            run_attempts += 1

        self.logger.debug(f"lean server output: {lean_output}")
        return lean_output

    @override
    def is_theorem_solved(self, repl_output) -> bool:
        return repl_output.lean_code_is_valid()
        # return not self.has_errors(repl_output) and "Goals accomplished" in repl_output["messages"][-1]

    @override
    def has_errors(self, repl_output) -> bool:
        for message in repl_output.messages:
            if (message.severity == "error" and not message.data.startswith("unsolved goals\n") and not
            message.data.startswith("unexpected end of input; expected '{'")):
                return True
        return False

        # if "messages" not in repl_output.keys():
        #     return False
        # for message in repl_output["messages"]:
        #     if message["severity"] == "error":
        #         return True
        # return False

    def __initialize_lean_environment(self):
        lean_config = LeanREPLConfig(project=TempRequireProject("mathlib"), verbose=True)
        self.lean_server = AutoLeanServer(lean_config)
        env_init_code = """
                import Mathlib
                import Aesop

                set_option maxHeartbeats 0

                open BigOperators Real Nat Topology Rat
                """
        env_init_lean_output = self.lean_server.run(Command(cmd=env_init_code, all_tactics=True))
        self.logger.debug(f"env init lean output: {env_init_lean_output}")
        self.env_number = env_init_lean_output.env

