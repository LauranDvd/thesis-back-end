# TODO move the test into a dedicated folder for integration tests
import json
import os

import boto3
import pytest
from dotenv import load_dotenv
from moto import mock_aws

from app import app, initialize

SUCCESSFUL_PROOF_REQUEST_STATUS_CODE = 202

load_dotenv()

@pytest.fixture
def client():
    app.config['TESTING'] = True
    return app.test_client()


def aws_mock():
    with mock_aws():
        sqs = boto3.client('sqs')
        created_queue = sqs.create_queue(QueueName='test_queue.fifo', Attributes={'FifoQueue': 'true'})
        queue_url = created_queue['QueueUrl']
        os.environ['THEOREM_SQS_URL'] = queue_url

        return sqs, queue_url


@mock_aws
def test_set_proof_successful(client):
    sqs_service, queue_url = aws_mock()
    initialize()
    theorem = """import Mathlib

theorem my_theorem (x : Nat) (h : x = 2 * 3) : x + 1 = 7 := by"""
    model = "pythia-410m-no-lora"
    request_query = {"theorem": theorem, "model": model}

    response = client.post('/proof', json=request_query)

    assert response.status_code == SUCCESSFUL_PROOF_REQUEST_STATUS_CODE
    messages_received_by_queue = sqs_service.receive_message(QueueUrl=queue_url)
    assert len(messages_received_by_queue['Messages']) == 1
    message_received = messages_received_by_queue['Messages'][0]
    message_body = json.loads(message_received['Body'])
    assert message_body['theorem'] == theorem
    assert message_body['model'] == model


def test_get_proof_no_model_provided(client):
    theorem = """import Mathlib

theorem my_theorem (x : Nat) (h : x = 2 * 3) : x + 1 = 7 := by
linarith"""

    request_query = {"theorem": theorem}
    response = client.get('/proof', query_string=request_query)
    assert response.status_code == 400


def test_get_proof_no_theorem_provided(client):
    model = "pythia-160M"
    request_query = {"model": model}
    response = client.get('/proof', query_string=request_query)
    assert response.status_code == 400

# TODO: test case with model that is not available
