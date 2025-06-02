from domain.EasyLogger import EasyLogger
from domain.language_model.model_factory.IModelAndTokenizerFactory import IModelAndTokenizerFactory

# TODO better few shot prompts
FORMALIZATION_PROMPT = r"""You are given a mathematical theorem in LaTeX format.
You need to formalize it into Lean 4 code. The theorem in LaTeX begins after [INFORMAL].
Write the formal statement after [FORMAL]. You need to provide exactly one formalized version. Begin with the "theorem" keyword. Do NOT prove anything.

[INFORMAL]
If \( x = 2 \cdot 3 \), then \( x + 1 = 7 \).
[FORMAL]
theorem example_theorem (x : Nat) (h : x = 2 * 3) : x + 1 = 7 := by

[INFORMAL]
{}
[FORMAL]
"""

DEFORMALIZATION_PROMPT = r"""You are given a mathematical proof in Lean 4.
You need to deformalize it into LaTeX. The proof in Lean 4 begins after [FORMAL].
Write the LaTeX proof after [INFORMAL]. You need to provide exactly one version.

[FORMAL]
theorem example_theorem (x : Nat) (h : x + 2 = 7) : x = 5 := by
  linarith
[INFORMAL]
Assuming \( x + 2 = 7 \), subtracting 2 from both sides gives \( x = 7 - 2 = 5 \).

[FORMAL]
{}
[INFORMAL]
"""

class FormalizationLanguageModel:
    def __init__(self, finetuned_model_path, device, model_and_tokenizer_factory: IModelAndTokenizerFactory):
        self.device = device
        self.logger = EasyLogger()
        self.tokenizer = model_and_tokenizer_factory.get_tokenizer(finetuned_model_path)
        self.model = model_and_tokenizer_factory.get_model(finetuned_model_path, device, len(self.tokenizer))

    def formalize_theorem_statement(self, informal_theorem_statement: str) -> str:
        prompt = FORMALIZATION_PROMPT.format(informal_theorem_statement)
        self.logger.debug(f"Formalizer prompt: {prompt}")

        # input_ids = self.tokenizer.encode(prompt, return_tensors='pt')
        # out = self.model.generate(
        #     input_ids,
        #     max_new_tokens=256,
        #     temperature=1,
        #     pad_token_id=self.tokenizer.eos_token_id
        # )
        #
        # formal_theorem_statement = self.tokenizer.decode(out[0], skip_special_tokens=True)
        formal_theorem_statement = """theorem example_theorem (x : Nat) (h : x + 2 = 7) : x = 5 := by"""

        self.logger.debug(f"Decoded model output: {formal_theorem_statement}")
        return formal_theorem_statement

    def deformalize_proof(self, formal_proof: str) -> str:
        prompt = DEFORMALIZATION_PROMPT.format(formal_proof)
        self.logger.debug(f"Formalizer prompt: {prompt}")

        # input_ids = self.tokenizer.encode(prompt, return_tensors='pt')
        # out = self.model.generate(
        #     input_ids,
        #     max_new_tokens=256,
        #     temperature=1,
        #     pad_token_id=self.tokenizer.eos_token_id
        # )
        #
        # informal_proof = self.tokenizer.decode(out[0], skip_special_tokens=True)
        informal_proof = r"""Assuming \( x + 2 = 7 \), subtracting 2 from both sides gives \( x = 7 - 2 = 5 \)."""

        self.logger.debug(f"Decoded model output: {informal_proof}")
        return informal_proof
