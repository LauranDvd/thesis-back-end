from unittest import TestCase
from unittest.mock import MagicMock

from api.TheoremQueue import TheoremQueue
from domain.EasyLogger import EasyLogger
from domain.lean.ILeanEvaluationInterpreter import ILeanEvaluationInterpreter
from domain.lean.ILeanEvaluator import ILeanEvaluator
from repository.TheoremRepository import TheoremRepository
from service.TheoremProvingService import TheoremProvingService


class TestTheoremProvingService(TestCase):
    def setUp(self):
        self.mock_lean_evaluator = MagicMock(spec=ILeanEvaluator)
        self.mock_lean_evaluation_interpreter = MagicMock(spec=ILeanEvaluationInterpreter)
        self.mock_theorem_queue = MagicMock(spec=TheoremQueue)
        self.mock_repository = MagicMock(spec=TheoremRepository)
        self.theorem_proving_service = TheoremProvingService(
            self.mock_lean_evaluator,
            self.mock_lean_evaluation_interpreter,
            self.mock_theorem_queue,
            self.mock_repository,
            EasyLogger()
        )

    def test_is_language_model_available_returns_repository_response(self):
        self.mock_repository.is_language_model_available.return_value = True
        self.assertTrue(self.theorem_proving_service.is_language_model_available("name"))

        self.mock_repository.is_language_model_available.return_value = False
        self.assertFalse(self.theorem_proving_service.is_language_model_available("name"))

    def test_send_proof_request_adds_to_queue_and_returns_proof_id(self):
        theorem = "import Mathlib\ntheorem ex"
        model = "model-name"
        user_id = "user-id"

        expected_proof_id = 12
        self.mock_repository.add_incomplete_proof.return_value = expected_proof_id
        actual_proof_id = self.theorem_proving_service.send_proof_request(theorem, model, user_id)

        self.mock_repository.add_incomplete_proof.assert_called_with(theorem, user_id, False)
        self.mock_theorem_queue.send_proof_request.assert_called_with(theorem, expected_proof_id, model)
        self.assertEqual(expected_proof_id, actual_proof_id)
