from domain.EasyLogger import EasyLogger
from exception.LeanException import LeanException
from exception.NotFoundClientRequestException import NotFoundClientRequestException
from service.TheoremProvingService import TheoremProvingService


class ProofSearchController:
    def __init__(self, theorem_proving_service: TheoremProvingService):
        self.__theorem_proving_service = theorem_proving_service
        self.__logger = EasyLogger()


    def handle_post_proof(self, theorem: str, model_short_name: str, user_id) -> int:
        if not theorem or theorem == "":
            raise NotFoundClientRequestException("No theorem provided")
        if not model_short_name or model_short_name == "":
            raise NotFoundClientRequestException("No language model name provided")

        if not self.__theorem_proving_service.is_language_model_available(model_short_name):
            raise NotFoundClientRequestException()

        is_code_valid, lean_error = self.__theorem_proving_service.is_lean_code_error_free(theorem)
        if not is_code_valid:
            raise LeanException(lean_error)

        proof_id = self.__theorem_proving_service.send_proof_request(theorem, model_short_name, user_id)
        self.__logger.debug(f"Proof ID for the received theorem: {proof_id}")

        return proof_id


    def handle_get_proof(self, proof_id: int) -> (bool, str):
        successful, found_proof = self.__theorem_proving_service.retrieve_complete_proof(proof_id)
        if found_proof is None:
            raise NotFoundClientRequestException()
        else:
            return successful, found_proof


    def handle_get_proof_informal(self, proof_id: int):
        informal_proof, was_successful, formalized_theorem, formal_proof = (
            self.__theorem_proving_service.retrieve_complete_informal_proof(proof_id))
        if formal_proof is None:
            raise NotFoundClientRequestException()
        else:
            return informal_proof, was_successful, formalized_theorem, formal_proof


    def handle_post_proof_informal(self, informal_theorem: str, model_short_name: str, user_id) -> int:
        if not informal_theorem or informal_theorem == "":
            raise NotFoundClientRequestException()
        if not model_short_name or model_short_name == "":
            raise NotFoundClientRequestException()

        self.__logger.info(f"Received informal theorem: {informal_theorem}. Requested model: {model_short_name}")

        if not self.__theorem_proving_service.is_language_model_available(model_short_name):
            raise NotFoundClientRequestException()

        proof_id = self.__theorem_proving_service.send_informal_proof_request(informal_theorem, user_id, model_short_name)
        self.__logger.debug(f"Proof ID for the received theorem: {proof_id}")

        return proof_id


    def handle_post_proof_fill(self, theorem_and_partial_proof: str, model_short_name: str, user_id) -> int:
        if not theorem_and_partial_proof or theorem_and_partial_proof == "":
            raise NotFoundClientRequestException()
        if not model_short_name or model_short_name == "":
            raise NotFoundClientRequestException()

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
