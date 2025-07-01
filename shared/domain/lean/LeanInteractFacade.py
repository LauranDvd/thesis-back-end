import subprocess
from typing import override

from lean_interact import LeanREPLConfig, TempRequireProject, AutoLeanServer, Command, LeanServer
from lean_interact.interface import LeanError, CommandResponse
from pydantic import PydanticUserError

from domain.EasyLogger import EasyLogger
from domain.lean.ILeanEvaluationInterpreter import ILeanEvaluationInterpreter
from domain.lean.ILeanEvaluator import ILeanEvaluator
from exception.LeanException import LeanException

UNSTARTED_PROOF_DEFAULT_ERROR = "unexpected end of input; expected '{'"

GOALS_LIST_MESSAGE_PREFIX = "unsolved goals\n"

ERROR_LEAN_MESSAGE_SEVERITY = "error"

UNKNOWN_ENVIRONMENT_LEAN_ERROR_MESSAGE = "Unknown environment."

ENV_INIT_CODE = """
                    import Mathlib
                    import Aesop

                    set_option maxHeartbeats 0

                    open BigOperators Real Nat Topology Rat
                    """


class LeanInteractFacade(ILeanEvaluator, ILeanEvaluationInterpreter):
    MAXIMUM_RUN_ATTEMPTS = 3
    RESET_CACHE_STEPS = 30

    def __init__(self, test_mode=False):
        self.__logger = EasyLogger()
        self.__test_mode = test_mode
        if not test_mode:
            self.__initialize_lean_environment()
        self.__reset_cache_count = 0

    @override
    def evaluate(self, lean_code: str):
        self.__logger.debug(f"Will run this Lean code: {lean_code}")

        self.__reset_cache_count += 1
        if self.__reset_cache_count == self.RESET_CACHE_STEPS and not self.__test_mode:
            self.__logger.debug(f"Will reset Lean cache")
            self.__initialize_lean_environment()
            self.__reset_cache_count = 0

        # lean_code = "import Mathlib\n\n" + lean_code

        ran_successfully = False
        run_attempts = 0
        lean_output = None
        while not ran_successfully and run_attempts < LeanInteractFacade.MAXIMUM_RUN_ATTEMPTS:
            self.__logger.debug(f"Will run code on the lean server")
            lean_output = self.__run_lean_code_safely(lean_code, True)
            self.__logger.debug(f"Finished running code on the lean server")
            if isinstance(lean_output, LeanError):
                if lean_output.message == UNKNOWN_ENVIRONMENT_LEAN_ERROR_MESSAGE:
                    self.__logger.debug(
                        "The Lean executor does not recognize the environment. Will reinitialize the environment.")
                    # self.__lean_server.clear_session_cache(force=True)
                    if not self.__test_mode:
                        self.__initialize_lean_environment()
            else:
                ran_successfully = True
            run_attempts += 1

        self.__logger.debug(f"lean server output: {lean_output}")
        return lean_output

    @override
    def is_theorem_solved(self, repl_output) -> bool:
        return repl_output.lean_code_is_valid()
        # return not self.has_errors(repl_output) and "Goals accomplished" in repl_output["messages"][-1]

    @override
    def has_errors(self, repl_output) -> bool:
        for message in repl_output.messages:
            if (message.severity == ERROR_LEAN_MESSAGE_SEVERITY and not message.data.startswith(GOALS_LIST_MESSAGE_PREFIX) and not
            message.data.startswith(UNSTARTED_PROOF_DEFAULT_ERROR)):
                return True
        return False

    @override
    def get_error(self, evaluation_output) -> str:
        self.__logger.debug(f"Will get error of this evaluation output: {evaluation_output}")
        for message in evaluation_output.messages:
            if (message.severity == ERROR_LEAN_MESSAGE_SEVERITY and not message.data.startswith(GOALS_LIST_MESSAGE_PREFIX) and not
            message.data.startswith(UNSTARTED_PROOF_DEFAULT_ERROR)):
                return message.data
        raise LeanException("There are no errors in the provided evaluation output")

    def __initialize_lean_environment(self):
        self.__logger.debug(f"Will run clear-lean-cache")
        try:
            subprocess.run(["clear-lean-cache"], check=True)
            self.__logger.debug(f"Finished running clear-lean-cache")
        except Exception as e:
            self.__logger.error(f"Could not complete clear-lean-cache: {e}")

        try:
            lean_config = LeanREPLConfig(project=TempRequireProject("mathlib"), verbose=True)
            # self.__lean_server = AutoLeanServer(lean_config)
            self.__lean_server = LeanServer(lean_config)
            # self.__lean_server.clear_session_cache(force=True)

        except (Exception, RuntimeError) as error:  # the library can throw many types of errors
            self.__logger.error(f"Initializing Lean env with lean-interact failed: {error}")
            self.__env_number = 0
            return

        self.__logger.debug("will run env init code on the Lean server")
        env_init_lean_output = self.__run_lean_code_safely(ENV_INIT_CODE, False)
        self.__logger.debug(f"env init lean output: {env_init_lean_output}")

        if isinstance(env_init_lean_output, LeanError):
            self.__env_number = 0
        else:
            self.__env_number = env_init_lean_output.env

    def __run_lean_code_safely(self, lean_code: str, use_env: bool) -> CommandResponse | LeanError:
        try:
            self.__logger.debug(f"Will run this code on the Lean server: {lean_code}")
            if use_env:
                return self.__lean_server.run(Command(cmd=lean_code, all_tactics=True, env=self.__env_number))
            else:
                return self.__lean_server.run(Command(cmd=lean_code, all_tactics=True))
        except (ValueError, PydanticUserError) as error:
            self.__logger.error(f"Running Lean code failed: {error}")
            return LeanError(message="The lean server returned an error")
