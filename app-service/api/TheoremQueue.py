import json
import os
import sys
import uuid
sys.path.append("/shared")

from botocore.client import BaseClient
from botocore.exceptions import ClientError

from domain.EasyLogger import EasyLogger

MESSAGE_GROUP_ID = "1"


class TheoremQueue:
    def __init__(self, sqs_client: BaseClient, sqs_url: str, logger: EasyLogger):
        self.__sqs_client: BaseClient = sqs_client
        self.__sqs_url = sqs_url
        self.__logger = logger

    def send_proof_request(self, theorem: str, proof_id: int, model: str):
        try:
            sqs_response = self.__sqs_client.send_message(
                QueueUrl=self.__sqs_url,
                MessageBody=json.dumps({'theorem': theorem, 'proof_id': proof_id, 'model': model, 'is_informal': False, 'is_fill': False}),
                MessageGroupId=MESSAGE_GROUP_ID,
                MessageDeduplicationId=str(uuid.uuid4())
            )
            self.__logger.debug(f"SQS response: {sqs_response}")
        except ClientError as error:
            self.__logger.error(f"Boto3 error when sending proof request: {error}")

    def send_proof_fill_request(self, theorem_with_partial_proof: str, proof_id: int, model: str):
        try:
            sqs_response = self.__sqs_client.send_message(
                QueueUrl=self.__sqs_url,
                MessageBody=json.dumps({'theorem': theorem_with_partial_proof, 'proof_id': proof_id, 'model': model, 'is_informal': False, 'is_fill': True}),
                MessageGroupId=MESSAGE_GROUP_ID,
                MessageDeduplicationId=str(uuid.uuid4())
            )
            self.__logger.debug(f"SQS response: {sqs_response}")
        except ClientError as error:
            self.__logger.error(f"Boto3 error when sending proof fill request: {error}")

    def send_informal_proof_request(self, informal_theorem: str, proof_id: int, model: str):
        try:
            sqs_response = self.__sqs_client.send_message(
                QueueUrl=self.__sqs_url,
                MessageBody=json.dumps({'theorem': informal_theorem, 'proof_id': proof_id, 'model': model, 'is_informal': True, 'is_fill': False}),
                MessageGroupId=MESSAGE_GROUP_ID,
                MessageDeduplicationId=str(uuid.uuid4())
            )
            self.__logger.debug(f"SQS response: {sqs_response}")
        except ClientError as error:
            self.__logger.error(f"Boto3 error when sending informal proof request: {error}")