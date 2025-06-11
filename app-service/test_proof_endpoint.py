# TODO move the test into a dedicated folder for integration tests

import pytest
from app import app
from config import MODEL_PATHS


# @pytest.fixture(scope='module', autouse=True)
# def update_model_paths():
#     print("hi")
#     MODEL_PATHS[
#         "pythia-160M"] = "/home/david/facultate/licenta_app/thesis-back-end/local_resources/language_models/pythia-160M-deduped/checkpoint-2000"
#     MODEL_PATHS[
#         "pythia-160M-lora"] = "/home/david/facultate/licenta_app/thesis-back-end/local_resources/language_models/id_2_pythia-160M-deduped_lora/checkpoint-2000"
#

@pytest.fixture
def client():
    print("hi")
    app.config['TESTING'] = True
    return app.test_client()


def test_get_proof(client):
    theorem = """import Mathlib

theorem my_theorem (x : Nat) (h : x = 2 * 3) : x + 1 = 7 := by"""
    model = "pythia-160M"

    request_query = {"theorem": theorem, "model": model}

    response = client.get('/proof', query_string=request_query)
    print(str(response.get_json()))

    assert response.status_code == 200
    response_json = response.get_json()
    assert response_json.keys() == ["proof", "successful"]


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
