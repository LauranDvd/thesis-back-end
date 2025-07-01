import json
import os

import boto3
import pytest
from dotenv import load_dotenv
from moto import mock_aws

from app import app, initialize
from domain.lean.MockLeanExecutor import THEOREM_AND_PARTIAL_PROOF_WITH_ERRORS, MOCK_LEAN_ERROR

POST_PROOF_SUCCESSFUL_REQUEST_STATUS_CODE = 202
GET_PROOF_SUCCESSFUL_REQUEST_STATUS_CODE = 200

load_dotenv()

# sqs_service: BaseClient
# queue_url: Any

@pytest.fixture
def client():
    with mock_aws():
        sqs = boto3.client('sqs')
        created_queue = sqs.create_queue(QueueName='test_queue.fifo', Attributes={'FifoQueue': 'true'})
        queue_url = created_queue['QueueUrl']
        os.environ['THEOREM_SQS_URL'] = queue_url

        app.config['TESTING'] = True
        initialize()
        yield app.test_client(), sqs, queue_url  # with "return", the real client will be used


def aws_mock():
    with mock_aws():
        sqs = boto3.client('sqs')
        created_queue = sqs.create_queue(QueueName='test_queue.fifo', Attributes={'FifoQueue': 'true'})
        queue_url = created_queue['QueueUrl']
        os.environ['THEOREM_SQS_URL'] = queue_url

        return sqs, queue_url


# @mock_aws
def test_post_proof_successful(client):
    client, sqs_service, queue_url = client

    theorem = """import Mathlib

theorem test_theorem (x : Nat) (h : x = 2 * 3) : x + 1 = 7 := by"""
    shortened_theorem = """theorem test_theorem (x : Nat) (h : x = 2 * 3) : x + 1 = 7 := by"""
    model = "pythia-410m-no-lora"
    request_query = {"theorem": theorem, "model": model}

    response = client.post('/proof', json=request_query)

    assert response.status_code == POST_PROOF_SUCCESSFUL_REQUEST_STATUS_CODE
    messages_received_by_queue = sqs_service.receive_message(QueueUrl=queue_url)
    print(f"messages received: {messages_received_by_queue}")
    assert len(messages_received_by_queue['Messages']) == 1
    message_received = messages_received_by_queue['Messages'][0]
    message_body = json.loads(message_received['Body'])
    assert message_body['theorem'] == shortened_theorem
    assert message_body['model'] == model


def test_post_proof_no_model_provided(client):
    client, sqs_service, queue_url = client

    theorem = """import Mathlib

theorem my_theorem (x : Nat) (h : x = 2 * 3) : x + 1 = 7 := by
linarith"""

    request_query = {"theorem": theorem}
    response = client.post('/proof', json=request_query)
    assert response.status_code == 404


def test_post_proof_no_theorem_provided(client):
    client, sqs_service, queue_url = client

    model = "pythia-160M"
    request_query = {"model": model}
    response = client.post('/proof', json=request_query)
    assert response.status_code == 404


def test_post_proof_fill_keeps_the_partial_proof(client):
    client, sqs_service, queue_url = client

    theorem_and_partial_proof = """import Mathlib

theorem test_theorem (x : Nat) (h : x = 2 * 3) : x + 1 = 7 := by
linarith"""
    model = "pythia-410m-no-lora"
    request_query = {"theorem_and_partial_proof": theorem_and_partial_proof, "model": model}

    response = client.post('/proof/fill', json=request_query)

    assert response.status_code == POST_PROOF_SUCCESSFUL_REQUEST_STATUS_CODE
    messages_received_by_queue = sqs_service.receive_message(QueueUrl=queue_url)
    print(f"messages received: {messages_received_by_queue}")
    assert len(messages_received_by_queue['Messages']) == 1
    message_received = messages_received_by_queue['Messages'][0]
    message_body = json.loads(message_received['Body'])
    assert message_body['theorem'] == theorem_and_partial_proof
    assert message_body['model'] == model


def test_post_proof_fill_returns_400_if_partial_proof_contains_errors(client):
    client, sqs_service, queue_url = client

    theorem_and_partial_proof = THEOREM_AND_PARTIAL_PROOF_WITH_ERRORS
    model = "pythia-410m-no-lora"
    request_query = {"theorem_and_partial_proof": theorem_and_partial_proof, "model": model}

    response = client.post('/proof/fill', json=request_query)

    assert response.status_code == 400
    assert response.json["lean_error"] == MOCK_LEAN_ERROR


def test_post_proof_informal_returns_proof_id(client):
    client, sqs_service, queue_url = client

    theorem = """if $x+1=2$ then $x=1$"""
    model = "pythia-410m-no-lora"
    request_query = {"informal_theorem": theorem, "model": model}

    response = client.post('/proof/informal', json=request_query)

    assert response.status_code == POST_PROOF_SUCCESSFUL_REQUEST_STATUS_CODE
    messages_received_by_queue = sqs_service.receive_message(QueueUrl=queue_url)
    print(f"messages received: {messages_received_by_queue}")
    assert len(messages_received_by_queue['Messages']) == 1
    message_received = messages_received_by_queue['Messages'][0]
    message_body = json.loads(message_received['Body'])
    assert message_body['model'] == model


def test_post_proof_informal_returns_404_if_model_not_available(client):
    client, sqs_service, queue_url = client

    theorem = """if $x+1=2$ then $x=1$"""
    model = "nonexistingmodel"
    request_query = {"informal_theorem": theorem, "model": model}

    response = client.post('/proof/informal', json=request_query)

    assert response.status_code == 404


def test_get_proof_by_id_returns_404_if_not_found(client):
    client, sqs_service, queue_url = client

    theorem = """import Mathlib

    theorem test_theorem (x : Nat) (h : x = 2 * 3) : x + 1 = 7 := by"""
    model = "pythia-410m-no-lora"
    request_query = {"theorem": theorem, "model": model}
    post_response = client.post('/proof', json=request_query)

    proof_id = post_response.json['proof_id']

    response = client.get(f'/proof/{proof_id}')

    assert response.status_code == 404


def test_get_proof_by_id_returns_proof_if_found(client):
    client, sqs_service, queue_url = client

    expected_proof = """theorem my_theorem (x : ℕ) (h : x = 2 * 3) : x + 1 = 7 := by

simd p"""
    response = client.get(f'/proof/96')

    assert response.status_code == GET_PROOF_SUCCESSFUL_REQUEST_STATUS_CODE
    assert response.json['proof'] == expected_proof


def test_get_informal_proof_by_id_returns_404_if_no_id_provided(client):
    client, sqs_service, queue_url = client

    response = client.get(f'/proof/informal/')

    assert response.status_code == 404


def test_get_informal_proof_by_id_returns_formal_and_informal_theorem_and_proof(client):
    client, sqs_service, queue_url = client

    original_proof = """theorem third_example (x : Nat) (h : x + 1 = 4) : x = 3 := by
nempSub"""
    response = client.get(f'/proof/informal/100')

    assert response.status_code == GET_PROOF_SUCCESSFUL_REQUEST_STATUS_CODE
    assert response.json['original_proof'] == original_proof
    assert response.json['successful'] == False


def test_get_proof_history_returns_list_of_proofs(client):
    client, sqs_service, queue_url = client

    response = client.get(f'/proof/history')

    assert response.status_code == 200
    assert 'proof_id' in response.json[0]
    assert 'formal_proof' in response.json[0]
    assert 'successful' in response.json[0]


def test_get_language_model_returns_list_of_models(client):
    client, sqs_service, queue_url = client

    response = client.get(f'/language_model')

    assert response.status_code == 200
    assert isinstance(response.json[0], str)