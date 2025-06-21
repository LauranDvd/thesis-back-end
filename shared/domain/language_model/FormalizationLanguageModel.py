from openai import OpenAI
from domain.EasyLogger import EasyLogger
from domain.lean.ILeanEvaluationInterpreter import ILeanEvaluationInterpreter
from domain.lean.ILeanEvaluator import ILeanEvaluator

# TODO better few shot prompts
FORMALIZATION_PROMPT = r"""You are given a mathematical theorem in LaTeX format.
You need to formalize it into Lean 4 code. The theorem in LaTeX begins after [INFORMAL].
Two examples are given. Write the formal statement after the last [FORMAL]. Begin with the `theorem` keyword. End with the `by` keyword. DO NOT include explanations. DO NOT include a proof.

[INFORMAL]
If \( x = 2 \cdot 3 \), then \( x + 1 = 7 \).
[FORMAL]
theorem first_example (x : Nat) (h : x = 2 * 3) : x + 1 = 7 := by

[INFORMAL]
Let \( f(x) \) be defined on the interval \((-1,1)\). Then \( f(x) \) can be expressed as the sum of an even function \( g(x) \) and an odd function \( h(x) \). Find \( g(x) \) and \( h(x) \).
[FORMAL]
theorem second_example (f : ℝ → ℝ) (x : ℝ) :
∃ g h : ℝ → ℝ, Even g ∧ Odd h ∧ f x = g x + h x ∧ g x = (f x + f (-x)) / 2 ∧ h x = (f x - f (-x)) / 2 := by

[INFORMAL]
{}
[FORMAL]
"""  # example taken from Goedel-Pset-v1 https://huggingface.co/datasets/Goedel-LM/Goedel-Pset-v1

DEFORMALIZATION_PROMPT = r"""You are given a mathematical proof in Lean 4.
You need to deformalize it into LaTeX. The proof in Lean 4 begins after [FORMAL].
Write the LaTeX proof after [INFORMAL]. You need to provide exactly one version.
Two examples are given. Write the LaTeX proof after the last [INFORMAL]. DO NOT include explanations. DO NOT include a proof.

[FORMAL]
theorem example_theorem (x : Nat) (h : x + 2 = 7) : x = 5 := by
  linarith
[INFORMAL]
Assuming \( x + 2 = 7 \), subtracting 2 from both sides gives \( x = 7 - 2 = 5 \).

[FORMAL]
theorem second_example (f : ℝ → ℝ) (x : ℝ) :
∃ g h : ℝ → ℝ, Even g ∧ Odd h ∧ f x = g x + h x ∧ g x = (f x + f (-x)) / 2 ∧ h x = (f x - f (-x)) / 2 := by
[INFORMAL]
Let \( f(x) \) be defined on the interval \((-1,1)\). Then \( f(x) \) can be expressed as the sum of an even function \( g(x) \) and an odd function \( h(x) \). Find \( g(x) \) and \( h(x) \).

[FORMAL]
{}
[INFORMAL]
"""


class FormalizationLanguageModel:
    MAXIMUM_NUMBER_OF_FORMALIZATION_ATTEMPTS = 8

    def __init__(
            self,
            model_name: str,
            openai_api_key: str,
            lean_evaluator: ILeanEvaluator,
            lean_evaluation_interpreter: ILeanEvaluationInterpreter
    ):
        self.__model_name = model_name
        self.__openai_client = OpenAI(api_key=openai_api_key)
        self.__logger = EasyLogger()
        self.__lean_evaluator = lean_evaluator
        self.__lean_evaluation_interpreter = lean_evaluation_interpreter

    def formalize_theorem_statement(self, informal_theorem_statement: str) -> (str, bool):
        prompt = FORMALIZATION_PROMPT.format(informal_theorem_statement)
        self.__logger.debug(f"Formalizer prompt: {prompt}")

        found_correct_formalization = False
        formal_theorem_statement = ""
        attempt_count = 0
        while not found_correct_formalization and attempt_count < FormalizationLanguageModel.MAXIMUM_NUMBER_OF_FORMALIZATION_ATTEMPTS:
            text_model_response = self.__query_model(prompt)
            self.__logger.debug(f"Formalization model response: {text_model_response}")

            formal_theorem_statement = text_model_response.split("[FORMAL]")[-1].strip()

            evaluation_output = self.__lean_evaluator.evaluate(formal_theorem_statement)
            if not self.__lean_evaluation_interpreter.has_errors(evaluation_output):
                found_correct_formalization = True
            attempt_count += 1

        return formal_theorem_statement, found_correct_formalization

    def deformalize_proof(self, formal_proof: str) -> (str, bool):
        # return "test response"

        prompt = DEFORMALIZATION_PROMPT.format(formal_proof)
        self.__logger.debug(f"Deformalizer prompt: {prompt}")

        text_model_response = self.__query_model(prompt)
        self.__logger.debug(f"Deformalization model response: {text_model_response}")
        return text_model_response.split("[INFORMAL]")[-1].strip(), True

    def __query_model(self, prompt):
        raw_model_response = self.__openai_client.chat.completions.create(
            model=self.__model_name,
            messages=[{"role": "user", "content": prompt}],
            temperature=1,
            max_tokens=512
        )
        return raw_model_response.choices[0].message.content
