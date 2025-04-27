from domain.language_model.IProofSearchLanguageModel import IProofSearchLanguageModel


class IModelConfiguration:
    def get_model_path(self) -> str:
        pass


    def get_language_model(self) -> IProofSearchLanguageModel:
        pass
