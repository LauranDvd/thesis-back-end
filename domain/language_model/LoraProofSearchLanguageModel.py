import random
import sys

import torch
import transformers
from peft import PeftModel, PeftConfig
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
import logging

from domain.EasyLogger import EasyLogger
from domain.language_model.IProofSearchLanguageModel import IProofSearchLanguageModel
from domain.lean.LeanUtilities import LeanUtilities

ERROR_TACTIC = "error_tactic"

class LoraProofSearchLanguageModel(IProofSearchLanguageModel):
    def __init__(self, finetuned_model_path, device):
        self.device = device
        self.tokenizer = transformers.GPTNeoXTokenizerFast.from_pretrained(finetuned_model_path)
        self.logger = EasyLogger.getLogger(logging.DEBUG, sys.stdout)

        config = PeftConfig.from_pretrained(finetuned_model_path)
        # quantization_config = BitsAndBytesConfig(load_in_8bit=True, device=device)

        base_model = transformers.GPTNeoXForCausalLM.from_pretrained(
            config.base_model_name_or_path,
            return_dict=True,
            # quantization_config=quantization_config
        ).to(device)
        base_model.resize_token_embeddings(len(self.tokenizer))

        self.model = PeftModel.from_pretrained(base_model, finetuned_model_path, device_map="auto").to(device)


    # TODO if possible, move to parent class
    def get_next_tactic(self, theorem: str) -> str:
        # return "ring" # TODO fix the REPL

        if theorem[-5:] == "sorry": # TODO ensure the program gets here without "sorry"
            theorem = theorem[:-6]
        formatted_theorem = LeanUtilities.build_formatted_program(theorem)

        self.logger.debug(f"Formatted theorem: {formatted_theorem}")

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
        if new_formatted_proof != LeanUtilities.ERROR_FORMATTED_PROGRAM:
            return next_tactic
        return ERROR_TACTIC

