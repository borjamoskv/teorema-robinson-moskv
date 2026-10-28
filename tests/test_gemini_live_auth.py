"""Authentication URL behavior for Gemini Live sessions."""

import importlib.util
import pathlib
import sys
import unittest
from urllib.parse import parse_qs, urlsplit

MODULE_PATH = (
    pathlib.Path(__file__).resolve().parents[1]
    / "src/03_state/scitt_ledger/scitt_python/bridges/gemini_live_client.py"
)
spec = importlib.util.spec_from_file_location("gemini_live_client", MODULE_PATH)
module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = module
spec.loader.exec_module(module)


class GeminiLiveAuthenticationTests(unittest.TestCase):
    def setUp(self):
        self.client = module.GeminiLiveClient(api_key="test-api-key")
        self.client.create_session("test-session")

    def test_ephemeral_url_uses_given_token_and_constrained_endpoint(self):
        token = "auth_tokens/example+with&characters"
        url = self.client.generate_websocket_url("test-session", ephemeral_token=token)
        parsed = urlsplit(url)
        self.assertTrue(parsed.path.endswith(".v1beta.GenerativeService.BidiGenerateContentConstrained"))
        self.assertEqual(parse_qs(parsed.query), {"access_token": [token]})
        self.assertNotIn(self.client.api_key, url)

    def test_missing_token_fails_closed(self):
        for token in (None, "", "  "):
            with self.subTest(token=token), self.assertRaises(ValueError):
                self.client.generate_websocket_url("test-session", ephemeral_token=token)

    def test_api_key_cannot_be_supplied_as_ephemeral_token(self):
        with self.assertRaises(ValueError):
            self.client.generate_websocket_url("test-session", ephemeral_token=self.client.api_key)

    def test_api_key_mode_uses_key_only(self):
        url = self.client.generate_websocket_url("test-session", use_ephemeral_token=False)
        parsed = urlsplit(url)
        self.assertTrue(parsed.path.endswith(".v1alpha.GenerativeService.BidiGenerateContent"))
        self.assertEqual(parse_qs(parsed.query), {"key": [self.client.api_key]})

    def test_api_key_mode_rejects_ambiguous_token(self):
        with self.assertRaises(ValueError):
            self.client.generate_websocket_url("test-session", False, ephemeral_token="token")

    def test_missing_session_and_missing_api_key_are_rejected(self):
        with self.assertRaises(KeyError):
            self.client.generate_websocket_url("missing", ephemeral_token="token")
        self.client.api_key = ""
        with self.assertRaises(ValueError):
            self.client.generate_websocket_url("test-session", False)


if __name__ == "__main__":
    unittest.main()
