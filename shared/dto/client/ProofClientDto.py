from dataclasses import dataclass

from repository.orm.Entities import ProofEntity, FormalizationEntity


@dataclass
class ProofClientDto:
    proof_id: int
    original_theorem_statement: str
    formal_proof: str
    did_user_provide_partial_proof: bool
    formalized_theorem_statement: str
    informal_proof: str
    successful: bool

    @classmethod
    def from_proof_entity(
            cls,
            proof_entity: ProofEntity,
            statement_formalization: FormalizationEntity,
            proof_formalization: FormalizationEntity
    ) -> "ProofClientDto":
        return ProofClientDto(
            proof_entity.proof_id,
            proof_entity.original_theorem_statement,
            proof_entity.formal_proof,
            proof_entity.did_user_provide_partial_proof,
            "" if statement_formalization is None else statement_formalization.formal_text,
            "" if proof_formalization is None else proof_formalization.informal_text,
            proof_entity.successful
        )


