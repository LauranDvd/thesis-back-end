import json
import logging
import subprocess
import sys

from domain.EasyLogger import EasyLogger


class LeanRepl:
    logger = EasyLogger.getLogger(logging.DEBUG, sys.stdout)

    @staticmethod
    def run_repl(lean_code: str) -> dict:
        file_path = "local_resources/file.lean"
        with open(file_path, "w") as f:
            f.write(lean_code)

        file_path_relative_to_repl = "../../local_resources/file.lean"
        repl_input = json.dumps({"path": file_path_relative_to_repl, "allTactics": True})
        LeanRepl.logger.debug(f"Will run REPL with input: {repl_input}")
        result = subprocess.run(  # TODO find a solution that doesn't run terminal commands
            ["lake", "exe", "repl"],
            input=repl_input,
            capture_output=True,
            text=True,
            cwd="external/repl/"
        )
        print(f"result stderr: {result.stderr}")

        try:
            return json.loads(result.stdout)  # Parse REPL output
        except json.JSONDecodeError:
            return {"error": "Invalid REPL output", "output": result.stdout}

    @staticmethod
    def does_repl_output_mean_solved(repl_output) -> bool:
        # the "sorry" we inserted at the end should result in an error
        # with data="no goals to be solved"
        if "messages" not in repl_output.keys():
            return False

        cnt_errors = 0
        error_message = ""
        for message in repl_output["messages"]:
            if message["severity"] == "error":
                cnt_errors += 1
                error_message = message

        if cnt_errors != 1:
            return False

        return error_message["data"] == "no goals to be solved"

    @staticmethod
    def repl_output_has_error_messages(repl_output: str) -> bool:
        if "messages" not in repl_output.keys():
            return False
        for message in repl_output["messages"]:
            if message["severity"] == "error":
                return True
        return False
