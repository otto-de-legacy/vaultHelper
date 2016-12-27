from mockito import mock
from mockito import unstub
from mockito import verify
from mockito import when, matchers

from vaultHelper.TokenSupplier import TokenSupplier
from vaultHelper.VaultService import VaultService

LABEL_DEVELOPMENT = "nonlive"
LABEL_PRODUCTION = "live"

VAULT_DEVELOPMENT = "https://development"
VAULT_PRODUCTION = "https://production"


class VaultTestHelper(object):
    def __init__(self, vaultMockConfig):
        self.mockConfig = vaultMockConfig
        self.mock_token_supplier()
        self.mock_vault_login_with_credentials()
        self.mock_vault_login_with_token()

    def mock_vault_login_with_credentials(self):
        username = self.mockConfig["credentials"]["username"]
        password = self.mockConfig["credentials"]["password"]

        clientmock1 = mock()
        clientmock1.token = self.mockConfig["tokens"][LABEL_DEVELOPMENT]
        clientmock2 = mock()
        clientmock2.token = self.mockConfig["tokens"][LABEL_PRODUCTION]

        when(VaultService).login_with_ldap(VAULT_DEVELOPMENT, username, password).thenReturn(clientmock1)
        when(VaultService).login_with_ldap(VAULT_PRODUCTION, username, password).thenReturn(clientmock2)

    def mock_vault_login_with_token(self):
        tokenForNonLive = self.mockConfig["tokens"][LABEL_DEVELOPMENT]
        when(VaultService).login_with_token(VAULT_DEVELOPMENT, tokenForNonLive).thenReturn(None)
        tokenForLive = self.mockConfig["tokens"][LABEL_PRODUCTION]
        when(VaultService).login_with_token(VAULT_PRODUCTION, tokenForLive).thenReturn(None)

    def mock_token_supplier(self):
        tokens = [{LABEL_DEVELOPMENT: {"VAULT_TOKEN": self.mockConfig["tokens"][LABEL_DEVELOPMENT]}},
                  {LABEL_PRODUCTION: {"VAULT_TOKEN": self.mockConfig["tokens"][LABEL_PRODUCTION]}}]
        when(TokenSupplier)._read().thenReturn(tokens)
        when(TokenSupplier).persist(matchers.any()).thenReturn(None)

    def set_secret(self, secretPath, secretValue):
        when(VaultService).read(secretPath).thenReturn(secretValue)

    def set_secret_list(self, secretParentPath, secretPaths):
        when(VaultService).list(secretParentPath).thenReturn(secretPaths)

    def set_write(self, secretPath, secretValue):
        when(VaultService).write(secretPath, secretValue).thenReturn(None)

    def set_delete(self, secretPath):
        when(VaultService).delete(secretPath).thenReturn(None)

    def verify_client_login(self, serverAddress, token):
        verify(VaultService, times=1).login_with_token(serverAddress, token)

    def verify_vault_read(self, secretPath):
        verify(VaultService, times=1).read(secretPath)

    def verify_vault_list(self, secretParentPath):
        verify(VaultService, times=1).list(secretParentPath)

    def verify_vault_write(self, secretPath, secretValue):
        verify(VaultService, times=1).write(secretPath, secretValue)

    def verify_vault_delete(self, secretPath):
        verify(VaultService, times=1).delete(secretPath)

    def destroy(self):
        unstub()
