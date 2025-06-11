from jinja2.lexer import TOKEN_DOT

from api.TheoremQueue import TheoremQueue
from domain.EasyLogger import EasyLogger
from domain.lean.ILeanEvaluationInterpreter import ILeanEvaluationInterpreter
from domain.lean.ILeanEvaluator import ILeanEvaluator
from repository import TheoremRepository
from repository.orm.Entities import ProofEntity


class TheoremProvingService:
    def __init__(
            self,
            lean_evaluator: ILeanEvaluator,
            lean_evaluation_interpreter: ILeanEvaluationInterpreter,
            theorem_queue: TheoremQueue, # TODO add the queue in the repo?
            theorem_repository: TheoremRepository,
            logger: EasyLogger
    ):
        self.__lean_evaluator = lean_evaluator
        self.__lean_evaluation_interpreter = lean_evaluation_interpreter
        self.__theorem_queue = theorem_queue
        self.__theorem_repository: TheoremRepository = theorem_repository
        self.__logger = logger

    def is_language_model_available(self, language_model_name: str):
        return self.__theorem_repository.is_language_model_available(language_model_name)

    def is_lean_code_error_free(self, code: str) -> (bool, str):
        # return False, "mock lean error"
        lean_evaluation_result = self.__lean_evaluator.evaluate(code)
        if self.__lean_evaluation_interpreter.has_errors(lean_evaluation_result):
            return False, self.__lean_evaluation_interpreter.get_error(lean_evaluation_result)
        return True, ""

    def send_proof_request(self, theorem: str, model: str):
        proof_id = self.__theorem_repository.add_incomplete_proof(theorem, False)
        self.__theorem_queue.send_proof_request(theorem, proof_id, model)
        return proof_id

    def send_informal_proof_request(self, informal_theorem: str, model: str):
        proof_id = self.__theorem_repository.add_incomplete_informal_proof(informal_theorem)
        self.__theorem_queue.send_informal_proof_request(informal_theorem, proof_id, model)
        return proof_id

    def send_proof_fill_request(self, theorem_with_partial_proof: str, model: str):
        proof_id = self.__theorem_repository.add_incomplete_proof(theorem_with_partial_proof, True)
        self.__theorem_queue.send_proof_fill_request(theorem_with_partial_proof, proof_id, model)
        return proof_id

    def retrieve_complete_proof(self, proof_id: int) -> (bool, str):
        proof: ProofEntity = self.__theorem_repository.retrieve_proof(proof_id)
        if proof.formal_proof == "" or proof.formal_proof is None:
            return False, None
        return proof.successful, proof.formal_proof

    def retrieve_complete_informal_proof(self, proof_id: int) -> (bool, str):
        proof: ProofEntity = self.__theorem_repository.retrieve_proof(proof_id)
        if proof.formal_proof == "" or proof.formal_proof is None:
            return None, False, None, None

        formalized_theorem = self.__theorem_repository.get_formalization(proof.statement_formalization_id).formal_text
        informal_proof = self.__theorem_repository.get_formalization(proof.proof_formalization_id).informal_text

        return informal_proof, proof.successful, formalized_theorem, proof.formal_proof


    def get_language_model_names(self) -> list[str]:
        return [model.model_name for model in self.__theorem_repository.get_language_models()]
