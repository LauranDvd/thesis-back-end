from typing import override

import torch
from transformers import GPTNeoXForCausalLM, GPTNeoXTokenizerFast

from domain.language_model.model_factory.IModelAndTokenizerFactory import IModelAndTokenizerFactory


class NonLoraModelAndTokenizerFactory(IModelAndTokenizerFactory):
    @override
    def get_model(self, model_path: str, base_model_name: str, device: str, token_embeddings_length: int = 0):
        print(f"load model: {model_path}")
        return GPTNeoXForCausalLM.from_pretrained(
            model_path,
            torch_dtype=torch.float16,
            device_map="auto"
        )

    @override
    def get_tokenizer(self, model_path: str, base_model_name: str):
        return GPTNeoXTokenizerFast.from_pretrained(base_model_name)
