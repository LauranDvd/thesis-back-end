import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

from domain.language_model.IProofSearchLanguageModel import IProofSearchLanguageModel


class SimpleProofSearchLanguageModel(IProofSearchLanguageModel):
    def __init__(self, model_name, device):
        self.device = device
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = (AutoModelForCausalLM.from_pretrained(model_name, torch_dtype=torch.float16, device_map="auto")
                 .to(device))

    def get_next_tactic(self, theorem: str) -> str:
        inputs = self.tokenizer(theorem, return_tensors="pt").to(self.device)

        with torch.no_grad():
            output = self.model.generate(**inputs, max_length=200)

        proof = self.tokenizer.decode(output[0], skip_special_tokens=True)
        return proof