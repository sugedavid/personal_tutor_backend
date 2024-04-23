import unittest
from unittest.mock import MagicMock, patch

from fastapi import HTTPException
from firebase_admin import auth, exceptions

from utils import get_db, validate_firebase_token


class TestUtils(unittest.IsolatedAsyncioTestCase):
    def test_get_db(self):
        mock_firestore_client = MagicMock()
        with unittest.mock.patch("utils.firestore.client", return_value=mock_firestore_client):
            db = get_db()
            self.assertEqual(db, mock_firestore_client)

    async def test_validate_firebase_token_success(self):
        mock_decoded_token = {"uid": "test_user_id"}
        mock_verify_id_token = MagicMock(return_value=mock_decoded_token)
        with patch.object(auth, "verify_id_token", mock_verify_id_token):
            token = "test_token"
            result = await validate_firebase_token(token)
            self.assertEqual(result, mock_decoded_token)

    async def test_validate_firebase_token_failure(self):
        mock_exception = "Firebase authentication failed"
        mock_verify_id_token = MagicMock(side_effect=exceptions.FirebaseError(code=401, message=mock_exception))
        with patch.object(auth, "verify_id_token", mock_verify_id_token):
            token = "invalid_token"
            with self.assertRaises(HTTPException) as context:
                await validate_firebase_token(token)
            self.assertEqual(context.exception.status_code, 401)
            self.assertIn(mock_exception, str(context.exception))