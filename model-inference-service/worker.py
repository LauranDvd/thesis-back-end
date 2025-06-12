import os
import sys
sys.path.append('../')

from sqlalchemy import create_engine

from domain.language_model.FormalizationLanguageModel import FormalizationLanguageModel
from repository.TheoremRepository import TheoremRepository
from service.FormalizationService import FormalizationService
from service.ModelService import ModelService
from domain.lean.LeanInteractFacade import LeanInteractFacade
from domain.lean.MockLeanExecutor import MockLeanExecutor


import boto3

from TheoremQueueListener import TheoremQueueListener
from domain.EasyLogger import EasyLogger

from dotenv import load_dotenv
from service.ProofSearchService import ProofSearchService

if __name__ == '__main__':
    load_dotenv()

    device = "cpu"

    sqs_url = os.environ["THEOREM_SQS_URL"]
    sqs_client = boto3.client('sqs')

    # lean_interact_facade = LeanInteractFacade()
    lean_interact_facade = MockLeanExecutor()

    formalization_language_model = FormalizationLanguageModel(
        "gpt-4.1-mini-2025-04-14",
        os.getenv('OPENAI_KEY'),
        lean_interact_facade,
        lean_interact_facade
    )
    formalization_service = FormalizationService(formalization_language_model)

    db_url = "postgresql://" + os.environ["AWS_RDS_USERNAME"] + ":" + os.environ["AWS_RDS_PASSWORD"] + \
             "@" + os.environ['AWS_RDS_ENDPOINT'] + ":" + os.environ['AWS_RDS_PORT'] + "/" + \
             os.environ['AWS_RDS_DB_NAME']
    db_engine = create_engine(db_url, pool_pre_ping=True)
    theorem_repository = TheoremRepository(db_engine, EasyLogger())

    model_service = ModelService(EasyLogger(), theorem_repository)

    model_short_name_to_config = model_service.get_model_short_name_to_config(device, lean_interact_facade,
                                                                              lean_interact_facade)
    proof_search_service = ProofSearchService(
        formalization_service,
        model_short_name_to_config,
        device
    )

    theorem_queue_listener = TheoremQueueListener(
        sqs_client,
        sqs_url,
        proof_search_service,
        theorem_repository,
        EasyLogger()
    )
    theorem_queue_listener.listen()
