from domain.language_model.FormalizationLanguageModel import FormalizationLanguageModel


class FormalizationService:
    def __init__(self, formalization_language_model: FormalizationLanguageModel):
        self.__formalization_language_model = formalization_language_model

    def formalize(self, informal_theorem: str) -> (str, bool):
        return self.__formalization_language_model.formalize_theorem_statement(informal_theorem)
