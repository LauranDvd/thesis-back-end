from unittest import TestCase
from unittest.mock import MagicMock, patch

from sqlalchemy import Engine
from sqlalchemy.exc import SQLAlchemyError

from domain.EasyLogger import EasyLogger
from repository.TheoremRepository import TheoremRepository
from repository.orm.Entities import ProofEntity, FormalizationEntity


class TestTheoremRepository(TestCase):
    def setUp(self):
        pass

    @patch('sqlalchemy.orm.Session.execute')
    def test_is_language_model_available_returns_true_if_model_exists(
        self,
        mock_execute: MagicMock
    ):
        mock_db_engine = MagicMock(Engine)
        mock_execute.return_value.scalar.return_value = ["name"]

        theorem_repository = TheoremRepository(
            mock_db_engine,
            EasyLogger()
        )
        self.assertTrue(theorem_repository.is_language_model_available("name"))

    @patch('sqlalchemy.orm.Session.execute')
    def test_is_language_model_available_returns_false_if_model_does_not_exist(
        self,
        mock_execute: MagicMock
    ):
        mock_db_engine = MagicMock(Engine)
        mock_execute.return_value.scalar.return_value = []

        theorem_repository = TheoremRepository(
            mock_db_engine,
            EasyLogger()
        )
        self.assertTrue(theorem_repository.is_language_model_available("name"))

    @patch('sqlalchemy.orm.Session.execute')
    def test_get_language_model_returns_empty_list_if_no_language_model(
            self,
            mock_execute: MagicMock
    ):
        mock_db_engine = MagicMock(Engine)
        mock_execute.return_value.all.return_value = []

        theorem_repository = TheoremRepository(
            mock_db_engine,
            EasyLogger()
        )
        self.assertListEqual(theorem_repository.get_language_models(), [])

    @patch('sqlalchemy.orm.Session.execute')
    def test_get_language_model_returns_models_from_database(
            self,
            mock_execute: MagicMock
    ):
        mock_db_engine = MagicMock(Engine)
        models_in_database = ["one", "two", "three"]
        mock_execute.return_value.all.return_value = [[model] for model in models_in_database]

        theorem_repository = TheoremRepository(
            mock_db_engine,
            EasyLogger()
        )
        self.assertListEqual(theorem_repository.get_language_models(), models_in_database)


    @patch('sqlalchemy.orm.Session')
    def test_add_incomplete_proof_successful(self, mock_session_class: MagicMock):
        mock_db_engine = MagicMock(Engine)

        mock_session = MagicMock()
        mock_session_class.return_value = mock_session

        expected_proof_id = 6
        def refresh(proof: ProofEntity):
            proof.proof_id = expected_proof_id
        mock_session.refresh.side_effect = refresh

        theorem_repository = TheoremRepository(
            mock_db_engine,
            EasyLogger()
        )

        session_local_mock = MagicMock()
        session_local_mock.return_value = mock_session
        theorem_repository._TheoremRepository__session_local = session_local_mock

        theorem = "the theorem"
        user_id = "abc"
        did_user_provide_partial_proof = False
        actual_proof_id = theorem_repository.add_incomplete_proof(
            theorem,
            user_id,
            did_user_provide_partial_proof
        )

        self.assertEqual(expected_proof_id, actual_proof_id)
        mock_session.add.assert_called_once()

    @patch('sqlalchemy.orm.Session')
    def test_add_incomplete_proof_returns_invalid_id_if_sql_fails(self, mock_session_class: MagicMock):
        mock_db_engine = MagicMock(Engine)

        mock_session = MagicMock()
        mock_session_class.return_value = mock_session

        mock_session.commit.side_effect = SQLAlchemyError()

        theorem_repository = TheoremRepository(
            mock_db_engine,
            EasyLogger()
        )

        session_local_mock = MagicMock()
        session_local_mock.return_value = mock_session
        theorem_repository._TheoremRepository__session_local = session_local_mock

        theorem = "the theorem"
        user_id = "abc"
        did_user_provide_partial_proof = False
        response = theorem_repository.add_incomplete_proof(
                theorem,
                user_id,
                did_user_provide_partial_proof
        )
        self.assertEqual(TheoremRepository.INVALID_ID, response)


    @patch('sqlalchemy.orm.Session')
    def test_get_formalization_returns_none_if_not_found(self, mock_session_class: MagicMock):
        mock_db_engine = MagicMock(Engine)

        mock_session = MagicMock()
        mock_session_class.return_value = mock_session

        mock_session.commit.side_effect = SQLAlchemyError()

        mock_session.execute.return_value.all.return_value = []

        theorem_repository = TheoremRepository(
            mock_db_engine,
            EasyLogger()
        )

        session_local_mock = MagicMock()
        session_local_mock.return_value = mock_session
        theorem_repository._TheoremRepository__session_local = session_local_mock

        formalization_id = 7
        response = theorem_repository.get_formalization(
            formalization_id
        )
        self.assertIsNone(response)


    @patch('sqlalchemy.orm.Session')
    def test_get_formalization_returns_formalization_if_found(self, mock_session_class: MagicMock):
        mock_db_engine = MagicMock(Engine)

        mock_session = MagicMock()
        mock_session_class.return_value = mock_session

        mock_session.commit.side_effect = SQLAlchemyError()

        formalization_id = 7
        expected_formalization_entity = FormalizationEntity(formalization_id=formalization_id, informal_text="abc", formal_text="def")
        mock_session.execute.return_value.all.return_value = [[expected_formalization_entity]]

        theorem_repository = TheoremRepository(
            mock_db_engine,
            EasyLogger()
        )

        session_local_mock = MagicMock()
        session_local_mock.return_value = mock_session
        theorem_repository._TheoremRepository__session_local = session_local_mock

        response: FormalizationEntity = theorem_repository.get_formalization(
            formalization_id
        )
        self.assertEqual(expected_formalization_entity, response)


