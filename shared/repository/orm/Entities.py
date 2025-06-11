from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class LanguageModelEntity(Base):
    __tablename__ = 'language_model'

    model_id = Column(Integer, primary_key=True, autoincrement=True)
    model_name = Column(String, unique=True)
    base_model_name = Column(String)
    used_lora = Column(Boolean)
    hf_path = Column(String)

class FormalizationEntity(Base):
    __tablename__ = 'formalization'

    formalization_id = Column(Integer, primary_key=True, autoincrement=True)
    informal_text = Column(String)
    formal_text = Column(String)


class ProofEntity(Base):
    __tablename__ = 'proof'

    proof_id = Column(Integer, primary_key=True, autoincrement=True)
    original_theorem_statement = Column(String)
    formal_proof = Column(String)
    did_user_provide_partial_proof = Column(Boolean)
    user_id = Column(Integer, ForeignKey('user.user_id'))
    statement_formalization_id = Column(Integer, ForeignKey('formalization.formalization_id'), nullable=True)
    proof_formalization_id = Column(Integer, ForeignKey('formalization.formalization_id'), nullable=True)
    successful = Column(Boolean)

class UserEntity(Base):
    __tablename__ = 'user'

    user_id = Column(Integer, primary_key=True, autoincrement=True)
    auth0_user_id = Column(String, unique=True)

    proofs = relationship('ProofEntity', back_populates='user')

ProofEntity.user = relationship('UserEntity', back_populates='proofs')