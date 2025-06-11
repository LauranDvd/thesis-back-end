from typing import overload

from sqlalchemy import create_engine, Engine, select
from sqlalchemy.orm import sessionmaker

from repository.orm.Entities import ProofEntity, LanguageModelEntity, FormalizationEntity

from service.InformalProofSearchResult import InformalProofSearchResult


class TheoremRepository:
    def __init__(self, db_engine: Engine):
        self.__db_engine = db_engine
        self.__session_local = sessionmaker(bind=db_engine)

    def is_language_model_available(self, model_name: str) -> bool:
        session = self.__session_local()
        try:
            statement = select(LanguageModelEntity).where(
                LanguageModelEntity.model_name == model_name
            )
            execution_result = session.execute(statement).scalar()
            return execution_result is not None
        finally:
            session.close()

    def get_language_models(self) -> list[LanguageModelEntity]:
        session = self.__session_local()
        try:
            statement = select(LanguageModelEntity)
            execution_result = session.execute(statement).all()
            return [row[0] for row in execution_result]
        finally:
            session.close()

    def retrieve_proof(self, proof_id: int) -> ProofEntity:
        session = self.__session_local()
        try:
            statement = select(ProofEntity).where(ProofEntity.proof_id == proof_id)
            execution_result = session.execute(statement).all()
            return [row[0] for row in execution_result][0]
        finally:
            session.close()

    def add_incomplete_proof(self, theorem: str, did_user_provide_partial_proof: bool) -> int:
        proof = ProofEntity(
            original_theorem_statement=theorem,
            formal_proof="",
            did_user_provide_partial_proof=did_user_provide_partial_proof,
            user_id=1,
            statement_formalization_id=None,
            proof_formalization_id=None
        )
        session = self.__session_local()

        try:
            session.add(proof)
            session.commit()
            session.refresh(proof)
        finally:
            session.close()

        return proof.proof_id

    def add_incomplete_informal_proof(self, informal_theorem: str) -> int:
        proof = ProofEntity(
            original_theorem_statement=informal_theorem,
            formal_proof="",
            did_user_provide_partial_proof=False,
            user_id=1,
            statement_formalization_id=None,
            proof_formalization_id=None
        )
        session = self.__session_local()

        try:
            session.add(proof)
            session.commit()
            session.refresh(proof)
        finally:
            session.close()

        return proof.proof_id

    def add_formalization(self, informal_text: str, formal_text: str) -> int:
        formalization = FormalizationEntity(
            informal_text=informal_text,
            formal_text=formal_text
        )
        session = self.__session_local()

        try:
            session.add(formalization)
            session.commit()
            session.refresh(formalization)
        finally:
            session.close()

        return formalization.formalization_id

    def get_formalization(self, formalization_id: int) -> FormalizationEntity:
        session = self.__session_local()
        try:
            statement = select(FormalizationEntity).where(FormalizationEntity.formalization_id == formalization_id)
            execution_result = session.execute(statement).all()
            return [row[0] for row in execution_result][0]
        finally:
            session.close()

    def update_complete_proof(self, proof_id, proof: str, successful: bool) -> None:
        session = self.__session_local()

        try:
            select_statement = select(ProofEntity).where(ProofEntity.proof_id == proof_id)
            old_proof_entity: ProofEntity = session.execute(select_statement).scalar()

            if old_proof_entity is None:
                raise ValueError(f"Proof with id={proof_id} does not exist")
            old_proof_entity.formal_proof = proof
            old_proof_entity.successful = successful

            session.commit()
        finally:
            session.close()

    def update_complete_informal_proof(
            self,
            proof_id: int,
            informal_proof_search_result: InformalProofSearchResult,
            statement_formalization_id: int,
            proof_deformalization_id: int,
            informal_theorem: str
    ):
        session = self.__session_local()

        try:
            select_statement = select(ProofEntity).where(ProofEntity.proof_id == proof_id)
            old_proof_entity: ProofEntity = session.execute(select_statement).scalar()

            if old_proof_entity is None:
                raise ValueError(f"Proof with id={proof_id} does not exist")

            old_proof_entity.successful = informal_proof_search_result.was_search_successful
            old_proof_entity.formal_proof = informal_proof_search_result.formal_proof
            old_proof_entity.proof_formalization_id = proof_deformalization_id
            old_proof_entity.original_theorem_statement = informal_theorem
            old_proof_entity.statement_formalization_id = statement_formalization_id

            session.commit()
        finally:
            session.close()

