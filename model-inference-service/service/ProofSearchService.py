import heapq

from domain.EasyLogger import EasyLogger
from domain.language_model.ProofSearchLanguageModel import ProofSearchLanguageModel
from domain.lean.ILeanEvaluationInterpreter import ILeanEvaluationInterpreter
from domain.lean.ILeanEvaluator import ILeanEvaluator
from domain.lean.LeanUtilities import LeanUtilities
from service.FormalizationService import FormalizationService
from service.InformalProofSearchResult import InformalProofSearchResult


class ProofSearchService:
    SEARCH_BUDGET = 50
    SEARCH_BUDGET_PER_STEP = 4

    def __init__(
            self,
            formalization_service: FormalizationService,
            lean_evaluator: ILeanEvaluator,
            lean_evaluation_interpreter: ILeanEvaluationInterpreter,
            model_short_name_to_config: dict,
            device
    ):
        self.__formalization_service = formalization_service
        self.__lean_evaluator = lean_evaluator
        self.__lean_evaluation_interpreter = lean_evaluation_interpreter
        self.__device = device
        self.__model_short_name_to_config = model_short_name_to_config
        self.__logger = EasyLogger()

    # theorem should start with "theorem " and end in ":= by"
    def search_proof(self, clean_theorem_statement: str, model_short_name: str) -> (str, bool):
        language_model = self.get_or_load_language_model(model_short_name)

        # full_proof = clean_theorem_statement

        initial_formatted_program = LeanUtilities.build_formatted_program(
            clean_theorem_statement,
            self.__lean_evaluator,
            self.__lean_evaluation_interpreter
        )

        if initial_formatted_program == LeanUtilities.PROVED_FORMATTED_PROGRAM:
            self.__logger.debug(
                f"Proof completed without generating any tactics.")
            return clean_theorem_statement, True

        queue = []
        heapq.heappush(queue, (0, (clean_theorem_statement, initial_formatted_program)))

        consumed_search_budget = 0

        while consumed_search_budget < ProofSearchService.SEARCH_BUDGET:
            popped_priority, (popped_full_program, popped_formatted_program) = heapq.heappop(queue)

            self.__logger.debug(f"Popped proof state priority={popped_priority}")
            self.__logger.debug(f"Full program: {popped_full_program}")
            self.__logger.debug(f"Formatted program: {popped_formatted_program}")

            found_valid_next_tactic = False
            while not found_valid_next_tactic and consumed_search_budget < ProofSearchService.SEARCH_BUDGET:
                next_tactics, next_tactics_scores = language_model.get_several_next_tactics(
                    popped_formatted_program,
                    ProofSearchService.SEARCH_BUDGET_PER_STEP
                )
                consumed_search_budget += ProofSearchService.SEARCH_BUDGET_PER_STEP

                for next_tactic, next_tactic_score in zip(next_tactics, next_tactics_scores):
                    new_full_program = popped_full_program + "\n" + next_tactic
                    new_formatted_program = LeanUtilities.build_formatted_program(
                        new_full_program,
                        self.__lean_evaluator,
                        self.__lean_evaluation_interpreter
                    )

                    if new_formatted_program == LeanUtilities.ERROR_FORMATTED_PROGRAM:
                        self.__logger.debug(f"This tactic resulted in an error. Will ignore it: {next_tactic}")
                        continue
                    if new_formatted_program == popped_formatted_program:
                        self.__logger.debug(f"This tactic did not change anything. Will ignore it: {next_tactic}")
                        continue

                    found_valid_next_tactic = True

                    self.__logger.debug(f"New full program: {new_full_program}")
                    self.__logger.debug(f"New formatted program: {new_formatted_program}")
                    self.__logger.debug(f"Score of this new tactic: {next_tactic_score}")

                    if new_formatted_program == LeanUtilities.PROVED_FORMATTED_PROGRAM:
                        self.__logger.debug(
                            f"Proof completed after generating a total of {consumed_search_budget} tactics.")
                        return new_full_program, True

                    heapq.heappush(queue,
                                   (popped_priority - next_tactic_score, (new_full_program, new_formatted_program))
                                   )

        self.__logger.debug(f"Didn't find a proof with search budget={ProofSearchService.SEARCH_BUDGET}")
        if queue == []:
            return clean_theorem_statement, False
        else:
            _, (popped_full_program, _) = heapq.heappop(queue)
            return popped_full_program, False

    def search_informal_proof(self, informal_statement: str, model_short_name: str) -> InformalProofSearchResult:
        # clean_theorem_statement = """theorem example_theorem (x : Nat) (h : x = 2 * 3) : x + 1 = 7 := by"""
        formal_statement, was_formalization_successful = self.__formalization_service.formalize(informal_statement)
        self.__logger.debug(
            f"Formalized version of user's informal theorem (successful: {was_formalization_successful}): {formal_statement}")

        if not was_formalization_successful:
            return InformalProofSearchResult(False, False, False, "", "", "")

        formal_proof, was_proof_search_successful = self.search_proof(formal_statement, model_short_name)
        if not was_proof_search_successful:
            return InformalProofSearchResult(True, False, False, formal_proof, "", formal_statement)

        informal_proof, was_deformalization_successful = self.__formalization_service.deformalize(formal_proof)
        if not was_deformalization_successful:
            return InformalProofSearchResult(True, True, False, formal_proof, informal_proof, formal_statement)
        self.__logger.debug(f"Informalized version of model's formal proof: {informal_proof}")

        return InformalProofSearchResult(True, True, True, formal_proof, informal_proof, formal_statement)

    def get_or_load_language_model(self, model_short_name: str) -> ProofSearchLanguageModel:
        return self.__model_short_name_to_config[model_short_name].get_language_model()

    def get_language_models(self):
        return list(self.__model_short_name_to_config.keys())
