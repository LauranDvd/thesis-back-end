from unittest import TestCase
from unittest.mock import MagicMock

from controller.ProofSearchController import ProofSearchController
from exception.NotFoundClientRequestException import NotFoundClientRequestException
from service.TheoremProvingService import TheoremProvingService


class TestProofSearchController(TestCase):
    def setUp(self):
        self.theorem_proving_service = MagicMock(spec=TheoremProvingService)
        self.proof_search_controller = ProofSearchController(self.theorem_proving_service)

    def test_handle_post_proof_raises_if_theorem_empty(self):
        with self.assertRaises(NotFoundClientRequestException) as exception_raised:
            self.proof_search_controller.handle_post_proof("", "model", "id")
        self.assertEqual(repr(NotFoundClientRequestException('No theorem provided')), repr(exception_raised.exception))

    def test_handle_post_proof_raises_if_model_empty(self):
        with self.assertRaises(NotFoundClientRequestException) as exception_raised:
            self.proof_search_controller.handle_post_proof("theorem", "", "id")
        self.assertEqual(repr(NotFoundClientRequestException('No language model name provided')), repr(exception_raised.exception))

    def test_handle_post_proof_raises_if_model_not_available(self):
        self.theorem_proving_service.is_language_model_available.return_value = False
        with self.assertRaises(NotFoundClientRequestException):
            self.proof_search_controller.handle_post_proof("theorem", "model", "id")

    def test_handle_post_proof_raises_if_the_theorem_field_does_not_contain_a_theorem(self):
        with self.assertRaises(NotFoundClientRequestException) as exception_raised:
            self.proof_search_controller.handle_post_proof("abcd", "model", "id")
        self.assertEqual(repr(NotFoundClientRequestException('No theorem in the Lean code')), repr(exception_raised.exception))

    def test_handle_post_proof_returns_proof_id_if_valid_theorem(self):
        self.theorem_proving_service.is_language_model_available.return_value = True
        expected_proof_id = 7
        self.theorem_proving_service.send_proof_request.return_value = expected_proof_id
        self.theorem_proving_service.is_lean_code_error_free.return_value = True, ""

        actual_proof_id = self.proof_search_controller.handle_post_proof("theorem abc : 1+1=2 := by", "model", "id")
        self.assertEqual(expected_proof_id, actual_proof_id)

    def test_handle_get_proof_raises_if_proof_not_complete(self):
        self.theorem_proving_service.retrieve_complete_proof.return_value = False, None
        with self.assertRaises(NotFoundClientRequestException) as exception_raised:
            self.proof_search_controller.handle_get_proof(12, "abc")

    def test_handle_get_proof_returns_proof_if_proof_complete(self):
        expected_successful = True
        expected_proof = "the proof"
        self.theorem_proving_service.retrieve_complete_proof.return_value = expected_successful, expected_proof

        actual_successful, actual_proof = self.proof_search_controller.handle_get_proof(12, "abc")

        self.assertEqual(expected_successful, expected_successful)
        self.assertEqual(expected_proof, actual_proof)