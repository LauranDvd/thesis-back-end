import json
import os
import re

from botocore.client import BaseClient

from domain.EasyLogger import EasyLogger
from service.ProofSearchService import ProofSearchService
from repository.TheoremRepository import TheoremRepository


class TheoremQueueListener:
    def __init__(
            self, sqs_client: BaseClient, sqs_url: str, proof_search_service: ProofSearchService,
            theorem_repository: TheoremRepository, logger: EasyLogger
    ):
        self.__sqs_client = sqs_client
        self.__sqs_url = sqs_url
        self.__proof_search_service = proof_search_service
        self.__theorem_repository = theorem_repository
        self.__logger = logger

    def listen(self):
        while True:
            queue_response = self.__sqs_client.receive_message(
                QueueUrl=self.__sqs_url,
                MaxNumberOfMessages=1,
                WaitTimeSeconds=20
            )
            if "Messages" not in queue_response:
                self.__logger.debug("No messages in queue yet.")
                continue
            message = queue_response["Messages"][0]["Body"]
            receipt_handle = queue_response["Messages"][0]["ReceiptHandle"]
            self.__logger.debug(f"Message received on SQS: {message}")

            self.__sqs_client.delete_message(
                QueueUrl=self.__sqs_url,
                ReceiptHandle=receipt_handle
            )
            self.__logger.debug(f"Message deleted from SQS: {receipt_handle}")

            # TODO check if it's informal or fill request

            message_json = json.loads(message)
            theorem = message_json["theorem"]
            model_short_name = message_json["model"]
            proof_id = int(message_json["proof_id"])
            is_informal = bool(message_json["is_informal"])
            is_fill = bool(message_json["is_fill"])

            self.__logger.debug(f"Will begin proof search for proof {proof_id}")
            if is_informal:
                informal_proof_search_result = self.__proof_search_service.search_informal_proof(
                    theorem,
                    model_short_name
                )
                statement_formalization_id = self.__theorem_repository.add_formalization(
                    theorem,
                    informal_proof_search_result.formal_theorem
                )
                proof_deformalization_id = self.__theorem_repository.add_formalization(
                    informal_proof_search_result.informal_proof,
                    informal_proof_search_result.formal_proof
                )

                self.__theorem_repository.update_complete_informal_proof(
                    proof_id,
                    informal_proof_search_result,
                    statement_formalization_id,
                    proof_deformalization_id,
                    theorem
                )
            elif is_fill:
                proof, successful = self.__proof_search_service.search_proof(
                    theorem,
                    model_short_name
                )
                self.__theorem_repository.update_complete_proof(
                    proof_id,
                    proof,
                    successful
                )
            else:
                theorem = self.__extract_theorem_statement(theorem)
                self.__logger.info(f"Cleaned theorem statement: {theorem}")

                proof, successful = self.__proof_search_service.search_proof(
                    theorem,
                    model_short_name
                )
                self.__theorem_repository.update_complete_proof(
                    proof_id,
                    proof,
                    successful
                )

    @staticmethod
    def __extract_theorem_statement(theorem: str) -> str: # TODO move this from here
        match = re.search(r'(theorem .*? by)', theorem)
        return match.group(1) if match else None
