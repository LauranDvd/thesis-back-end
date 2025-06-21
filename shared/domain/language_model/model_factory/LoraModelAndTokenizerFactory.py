from typing import override

import transformers
from peft import PeftConfig, PeftModel

from domain.language_model.model_factory.IModelAndTokenizerFactory import IModelAndTokenizerFactory


class LoraModelAndTokenizerFactory(IModelAndTokenizerFactory):
    @override
    def get_model(self, model_path: str, base_model_name: str, device: str, token_embeddings_length: int = 0):
        config = PeftConfig.from_pretrained(model_path)
        # quantization_config = BitsAndBytesConfig(load_in_8bit=True, device=device)

        base_model = transformers.GPTNeoXForCausalLM.from_pretrained(
            config.base_model_name_or_path,
            return_dict=True,
            # quantization_config=quantization_config
        ).to(device)
        base_model.resize_token_embeddings(token_embeddings_length)

        print(f"will load peftmodel from path {model_path} with base model {base_model_name}")
        return PeftModel.from_pretrained(base_model, model_path, device_map="auto").to(device)

    @override
    def get_tokenizer(self, model_path: str, base_model_name: str):
        return transformers.GPTNeoXTokenizerFast.from_pretrained(model_path)
