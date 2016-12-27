import os
from unittest import TestCase

from vaultHelper.TokenSupplier import TokenSupplier


class TestTokenSupplier(TestCase):
    def setUp(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        self.tokens_file_path = current_dir + "/.myVault/vaultTokens.json"

    def tearDown(self):
        os.remove(self.tokens_file_path)

    def test_persist(self):
        # given
        tokens = [{"nonlive": {"VAULT_TOKEN": "someTokenForNonLive"}},
                  {"live": {"VAULT_TOKEN": "someTokenForLive"}}]

        supplier = TokenSupplier(self.tokens_file_path)
        # when

        supplier.persist(tokens)

        # then
        self.assertTrue(os.path.isfile(self.tokens_file_path))

        persisted_tokens = supplier._read()
        self.assertEquals(tokens, persisted_tokens)
