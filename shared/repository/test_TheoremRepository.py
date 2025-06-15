from unittest import TestCase
from unittest.mock import MagicMock, patch

from sqlalchemy import Engine

from domain.EasyLogger import EasyLogger
from repository.TheoremRepository import TheoremRepository


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
