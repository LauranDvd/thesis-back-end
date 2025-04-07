import logging
import sys
import random

import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

from domain.EasyLogger import EasyLogger
from domain.language_model.IProofSearchLanguageModel import IProofSearchLanguageModel
from domain.language_model.LoraProofSearchLanguageModel import ERROR_TACTIC
from domain.lean.LeanUtilities import LeanUtilities, ERROR_FORMATTED_PROGRAM

THEOREM_WAS_PROVED_TACTIC = "theorem_already_proved"

class SimpleProofSearchLanguageModel(IProofSearchLanguageModel):
    def __init__(self, model_name, device):
        self.device = device
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = (AutoModelForCausalLM.from_pretrained(model_name, torch_dtype=torch.float16, device_map="auto")
                 .to(device))
        self.logger = EasyLogger.getLogger(logging.DEBUG, sys.stdout)


    def get_next_tactic(self, theorem: str) -> str:
        if theorem[-5:] == "sorry":  # TODO ensure the program gets here without "sorry"
            theorem = theorem[:-6]

        formatted_theorem = LeanUtilities.build_formatted_program(theorem)

        self.logger.debug(f"Formatted theorem: {formatted_theorem}")

        if formatted_theorem == LeanUtilities.PROVED_FORMATTED_PROGRAM:
            return THEOREM_WAS_PROVED_TACTIC

        # inputs = self.tokenizer.encode(formatted_theorem, return_tensors="pt").to(self.device)
        #
        # with torch.no_grad():
        #     output = self.model.generate(**inputs, max_length=200)
        #     self.model.generate(inputs, max_new_tokens=256, pad_token_id=self.tokenizer.eos_token_id)
        #
        # next_tactic = self.tokenizer.decode(output[0][inputs.shape[1]:], skip_special_tokens=True)

        input_ids = self.tokenizer.encode(formatted_theorem, return_tensors='pt')
        out = self.model.generate(
            input_ids,
            max_new_tokens=256,
            num_return_sequences=3,
            do_sample=True,
            temperature=1,
            pad_token_id=self.tokenizer.eos_token_id
        )

        next_tactic = self.tokenizer.decode(random.choice(out)[input_ids.shape[1]:], skip_special_tokens=True)
        self.logger.debug(f"decoded model output: {next_tactic}")

        new_proof = theorem + "\n" + next_tactic
        new_formatted_proof = LeanUtilities.build_formatted_program(new_proof)
        if new_formatted_proof != ERROR_FORMATTED_PROGRAM:
            return next_tactic
        return ERROR_TACTIC