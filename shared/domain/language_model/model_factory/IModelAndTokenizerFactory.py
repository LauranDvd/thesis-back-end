class IModelAndTokenizerFactory:
    def get_model(self, model_path: str, base_model_name: str, device: str, token_embeddings_length: int = 0):
        pass

    def get_tokenizer(self, model_path: str, base_model_name: str):
        pass
