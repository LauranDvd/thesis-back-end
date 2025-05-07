from typing import override

import torch
import transformers
from transformers import AutoModelForCausalLM, AutoTokenizer

from domain.language_model.model_factory.IModelAndTokenizerFactory import IModelAndTokenizerFactory


class NonLoraModelAndTokenizerFactory(IModelAndTokenizerFactory):
    @override
    def get_model(self, model_path: str, device: str, token_embeddings_length: int = 0):
        return (AutoModelForCausalLM.from_pretrained(model_path, torch_dtype=torch.float16, device_map="auto")
                 .to(device))

    @override
    def get_tokenizer(self, model_path: str):
        return AutoTokenizer.from_pretrained(model_path)
