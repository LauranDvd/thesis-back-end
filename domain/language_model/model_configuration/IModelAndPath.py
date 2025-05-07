from domain.language_model.ProofSearchLanguageModel import ProofSearchLanguageModel


class IModelAndPath:
    def get_model_path(self) -> str:
        pass


    def get_language_model(self) -> ProofSearchLanguageModel:
        pass
