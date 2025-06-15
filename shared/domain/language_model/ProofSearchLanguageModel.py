import logging
import sys
import random

import torch

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

    def get_several_next_tactics(self, goals: str, number_of_tactics: int) -> tuple[list[str], list[float]]:
        inputs = self.__tokenizer.encode(goals, return_tensors="pt").to(self.__device)

        tactics, scores = [], []
        output = self.__model.generate(inputs, max_new_tokens=256, pad_token_id=self.__tokenizer.eos_token_id,
                                       num_return_sequences=number_of_tactics,
                                       # num_beams=number_of_tactics,
                                       return_dict_in_generate=True,
                                       do_sample=True,
                                       output_scores=True,
                                       temperature=1
                                       )

        output_tokens = output.sequences[:, inputs.shape[1]:]
        tactics.extend(self.__tokenizer.batch_decode(
            output_tokens,
            skip_special_tokens=True
        ))
        # scores.extend([0 for _ in range(number_of_tactics)])

        if output.scores:
            self.__logger.debug("Will compute scores of the model's output")
            new_scores = []
            for tactic_index in range(number_of_tactics):
                tactic_log_prob = 0
                generated_tokens = output_tokens[tactic_index]
                for step in range(generated_tokens.shape[0]):
                    if step >= len(output.scores):
                        break
                    token_id = generated_tokens[step].item()
                    token_scores = output.scores[step]
                    log_prob = torch.nn.functional.log_softmax(token_scores, dim=-1)
                    tactic_log_prob += log_prob[tactic_index, token_id].item()
                    if token_id == self.__tokenizer.eos_token_id:
                        break
                new_scores.append(tactic_log_prob)
            scores.extend(new_scores)
            self.__logger.debug("Computed scores for model's output")
        else:
            self.__logger.warn("Model output has no scores")
            scores.extend([0 for _ in range(number_of_tactics)])

        return tactics, scores
