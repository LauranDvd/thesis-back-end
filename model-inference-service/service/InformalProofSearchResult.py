from dataclasses import dataclass


@dataclass
class InformalProofSearchResult:
    was_formalization_successful: bool
    was_search_successful: bool
    was_deformalization_successful: bool
    formal_proof: str
    informal_proof: str
    formal_theorem: str
