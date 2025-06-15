import logging
import sys
import random

from domain.EasyLogger import EasyLogger
from domain.language_model.model_factory import IModelAndTokenizerFactory
from domain.lean.ILeanEvaluationInterpreter import ILeanEvaluationInterpreter
from domain.lean.ILeanEvaluator import ILeanEvaluator
from domain.lean.LeanUtilities import LeanUtilities

ERROR_TACTIC = "error_tactic"
THEOREM_WAS_PROVED_TACTIC = "theorem_already_proved"


class ProofSearchLanguageModel:
    def __init__(
            self, finetuned_model_path, base_model_name: str, device,
            model_and_tokenizer_factory: IModelAndTokenizerFactory,
            lean_evaluator: ILeanEvaluator,
            lean_evaluation_interpreter: ILeanEvaluationInterpreter
    ):
        self.__device = device
        self.__logger = EasyLogger()
        self.__tokenizer = model_and_tokenizer_factory.get_tokenizer(finetuned_model_path, base_model_name)
        self.__model = model_and_tokenizer_factory.get_model(finetuned_model_path, base_model_name, device,
                                                             len(self.__tokenizer))
        self.__lean_evaluator = lean_evaluator
        self.__lean_evaluation_interpreter = lean_evaluation_interpreter

    def get_next_tactic(self, theorem: str) -> str:
        if theorem[-5:] == "sorry":  # TODO ensure the program gets here without "sorry"
            theorem = theorem[:-6]
        formatted_theorem = LeanUtilities.build_formatted_program(theorem, self.__lean_evaluator,
                                                                  self.__lean_evaluation_interpreter)

        self.__logger.debug(f"Formatted theorem: {formatted_theorem}")

        if formatted_theorem == LeanUtilities.PROVED_FORMATTED_PROGRAM:
            return THEOREM_WAS_PROVED_TACTIC

        input_ids = self.__tokenizer.encode(formatted_theorem, return_tensors='pt')
        out = self.__model.generate(
            input_ids,
            max_new_tokens=256,
            num_return_sequences=3,
            do_sample=True,
            temperature=1,
            pad_token_id=self.__tokenizer.eos_token_id
        )

        next_tactic = self.__tokenizer.decode(random.choice(out)[input_ids.shape[1]:], skip_special_tokens=True)
        self.__logger.debug(f"decoded model output: {next_tactic}")

        new_proof = theorem + "\n" + next_tactic
        new_formatted_proof = LeanUtilities.build_formatted_program(new_proof, self.__lean_evaluator,
                                                                    self.__lean_evaluation_interpreter)
        if new_formatted_proof != LeanUtilities.ERROR_FORMATTED_PROGRAM:
            return next_tactic
        return ERROR_TACTIC
