from domain.EasyLogger import EasyLogger
from domain.lean.LeanUtilities import LeanUtilities
from exception.LeanException import LeanException
from exception.NotFoundClientRequestException import NotFoundClientRequestException
from service.TheoremProvingService import TheoremProvingService


class ProofSearchController:
    def __init__(self, theorem_proving_service: TheoremProvingService):
        self.__theorem_proving_service = theorem_proving_service
        self.__logger = EasyLogger()


    def handle_post_proof(self, theorem: str, model_short_name: str, user_id) -> int:
        ProofSearchController.__validate_string_not_empty(theorem, "No theorem provided")
        ProofSearchController.__validate_string_not_empty(model_short_name, "No language model name provided")

        if not self.__theorem_proving_service.is_language_model_available(model_short_name):
            raise NotFoundClientRequestException()

        theorem = LeanUtilities.extract_theorem_statement(theorem)
        if theorem is None:
            raise NotFoundClientRequestException("No theorem in the Lean code")
        is_code_valid, lean_error = self.__theorem_proving_service.is_lean_code_error_free(theorem)
        if not is_code_valid:
            raise LeanException(lean_error)

        proof_id = self.__theorem_proving_service.send_proof_request(theorem, model_short_name, user_id)
        self.__logger.debug(f"Proof ID for the received theorem: {proof_id}")

        return proof_id


    def handle_get_proof(self, proof_id: int, user_id: str) -> (bool, str):
        successful, found_proof = self.__theorem_proving_service.retrieve_complete_proof(proof_id, user_id)
        if found_proof is None:
            raise NotFoundClientRequestException()
        else:
            return successful, found_proof


    def handle_get_proof_informal(self, proof_id: int, user_id: str):
        informal_proof, was_successful, formalized_theorem, formal_proof = (
            self.__theorem_proving_service.retrieve_complete_informal_proof(proof_id, user_id))
        if formal_proof is None:
            raise NotFoundClientRequestException()
        else:
            return informal_proof, was_successful, formalized_theorem, formal_proof


    def handle_post_proof_informal(self, informal_theorem: str, model_short_name: str, user_id) -> int:
        ProofSearchController.__validate_string_not_empty(informal_theorem, "No theorem provided")
        ProofSearchController.__validate_string_not_empty(model_short_name, "No model provided")

        self.__logger.info(f"Received informal theorem: {informal_theorem}. Requested model: {model_short_name}")

        if not self.__theorem_proving_service.is_language_model_available(model_short_name):
            raise NotFoundClientRequestException()

        proof_id = self.__theorem_proving_service.send_informal_proof_request(informal_theorem, user_id, model_short_name)
        self.__logger.debug(f"Proof ID for the received theorem: {proof_id}")

        return proof_id


    def handle_post_proof_fill(self, theorem_and_partial_proof: str, model_short_name: str, user_id) -> int:
        ProofSearchController.__validate_string_not_empty(theorem_and_partial_proof, "No theorem provided")
        ProofSearchController.__validate_string_not_empty(model_short_name, "No model provided")

        if not self.__theorem_proving_service.is_language_model_available(model_short_name):
            raise NotFoundClientRequestException()

        is_code_valid, lean_error = self.__theorem_proving_service.is_lean_code_error_free(theorem_and_partial_proof)
        if not is_code_valid:
            raise LeanException(lean_error)

        proof_id = self.__theorem_proving_service.send_proof_fill_request(theorem_and_partial_proof, user_id, model_short_name)
        self.__logger.debug(f"Proof ID for the received theorem: {proof_id}")

        return proof_id


    def handle_get_proof_history(self, user_id: int) -> (bool, int):
        self.__logger.debug(f"Getting proof history for user {user_id}")
        proof_history = self.__theorem_proving_service.get_proof_history(user_id)
        self.__logger.debug(f"Will return proof history of size {len(proof_history)} to user {user_id}")
        return proof_history

    @staticmethod
    def __validate_string_not_empty(string: str, error_message: str):
        if not string or string == "":
            raise NotFoundClientRequestException(error_message)
