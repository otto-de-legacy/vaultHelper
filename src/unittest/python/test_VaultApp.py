import os
from unittest import TestCase

from click.testing import CliRunner
from mockito import verify
from mockito import when

from VaultTestHelper import VaultTestHelper
from vaultHelper.Policy import Policy
from vaultHelper.PolicyService import PolicyService

from vaultHelper.VaultApp import cli

SOME_USERNAME = "someUsername"
SOME_PASSWD = "somePasswd"

SOME_TOKEN_FOR_NONLIVE = "someTokenForNonLive"
SOME_TOKEN_FOR_LIVE = "someTokenForLive"

SOME_CI_SECRET_PATH = "ci/myTeam/myService/mongo.password"
ANOTHER_CI_SECRET_PATH = "ci/myTeam/myService/jdbc.password"
SOME_CI_SECRET_PARENT_PATH = "ci/myTeam/myService"

SOME_DEVELOP_SECRET_PATH = "develop/myTeam/myService/mongo.password"
SOME_DEVELOP_SECRET_PARENT_PATH = "develop/myTeam/myService"

SOME_NONLIVE_SECRET_PATH = "nonlive/myTeam/myService/mongo.password"
SOME_NONLIVE_SECRET_PARENT_PATH = "nonlive/myTeam/myService"

SOME_SECRET_VALUE = "guessIt"

VAULT_MOCK_CONFIG = {
    "credentials": {
        "username": SOME_USERNAME,
        "password": SOME_PASSWD
    },
    "serverAddress": {
        "nonlive": "https://development",
        "live": "https://production"
    },
    "tokens": {"nonlive": SOME_TOKEN_FOR_NONLIVE,
               "live": SOME_TOKEN_FOR_LIVE}
}


class TestVaultApp(TestCase):
    def setUp(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        self.config_path = current_dir + "/.myVault/myVault.cfg"
        self.vault_mock = VaultTestHelper(VAULT_MOCK_CONFIG)

    def tearDown(self):
        self.vault_mock.destroy()

    def test_login(self):
        # given
        runner = CliRunner()

        # when
        result = runner.invoke(cli,
                               ["login", "--ldapusername", SOME_USERNAME, "--ldappassword", SOME_PASSWD,
                                "--config_path", self.config_path])

        # then
        self.assertIs(result.exit_code, 0, result.exception)
        self.assertIn("Got token " + SOME_TOKEN_FOR_NONLIVE + " for nonlive", str(result.output))
        self.assertIn("Got token " + SOME_TOKEN_FOR_LIVE + " for live", str(result.output))

    def test_read(self):
        # given
        self.vault_mock.set_secret(SOME_CI_SECRET_PATH, SOME_SECRET_VALUE)

        # when
        runner = CliRunner()
        result = runner.invoke(cli, ["read", "--path", SOME_CI_SECRET_PATH, "--config_path", self.config_path])

        # then
        self.assertIs(0, result.exit_code, result.exception)
        self.assertIn(SOME_SECRET_VALUE, str(result.output))
        self.vault_mock.verify_client_login("https://development", SOME_TOKEN_FOR_NONLIVE)
        self.vault_mock.verify_vault_read(SOME_CI_SECRET_PATH)

    def test_read_with_nonlive_label(self):
        # given
        self.vault_mock.set_secret(SOME_CI_SECRET_PATH, SOME_SECRET_VALUE)
        self.vault_mock.set_secret(SOME_DEVELOP_SECRET_PATH, SOME_SECRET_VALUE)

        # when
        runner = CliRunner()
        result = runner.invoke(cli, ["read", "--path", SOME_NONLIVE_SECRET_PATH, "--config_path", self.config_path])

        # then
        self.assertIs(0, result.exit_code, result.exception)
        self.assertIn(SOME_SECRET_VALUE, str(result.output))
        self.vault_mock.verify_client_login("https://development", SOME_TOKEN_FOR_NONLIVE)
        self.vault_mock.verify_vault_read(SOME_CI_SECRET_PATH)
        self.vault_mock.verify_vault_read(SOME_DEVELOP_SECRET_PATH)

    def test_list(self):
        # given
        self.vault_mock.set_secret_list(SOME_CI_SECRET_PARENT_PATH, [SOME_CI_SECRET_PATH, ANOTHER_CI_SECRET_PATH])
        # when
        runner = CliRunner()
        result = runner.invoke(cli, ["list", "--path", SOME_CI_SECRET_PARENT_PATH, "--config_path", self.config_path])

        # then
        self.assertIs(0, result.exit_code, result.exception)
        self.assertIn(SOME_CI_SECRET_PATH, str(result.output))
        self.assertIn(ANOTHER_CI_SECRET_PATH, str(result.output))
        self.vault_mock.verify_client_login("https://development", SOME_TOKEN_FOR_NONLIVE)
        self.vault_mock.verify_vault_list(SOME_CI_SECRET_PARENT_PATH)

    def test_list_with_nonlive_label(self):
        # given
        self.vault_mock.set_secret_list(SOME_CI_SECRET_PARENT_PATH, [SOME_CI_SECRET_PATH, ANOTHER_CI_SECRET_PATH])
        self.vault_mock.set_secret_list(SOME_DEVELOP_SECRET_PARENT_PATH, [SOME_DEVELOP_SECRET_PATH])

        # when
        runner = CliRunner()
        result = runner.invoke(cli, ["list", "--path", SOME_NONLIVE_SECRET_PARENT_PATH,
                                     "--config_path", self.config_path])

        # then
        self.assertIs(0, result.exit_code, result.exception)
        self.assertIn(SOME_CI_SECRET_PATH, str(result.output))
        self.assertIn(ANOTHER_CI_SECRET_PATH, str(result.output))
        self.assertIn(SOME_DEVELOP_SECRET_PATH, str(result.output))

        self.vault_mock.verify_client_login("https://development", SOME_TOKEN_FOR_NONLIVE)
        self.vault_mock.verify_vault_list(SOME_CI_SECRET_PARENT_PATH)
        self.vault_mock.verify_vault_list(SOME_DEVELOP_SECRET_PARENT_PATH)

    def test_write(self):
        # given
        self.vault_mock.set_write(SOME_CI_SECRET_PATH, SOME_SECRET_VALUE)

        # when
        runner = CliRunner()
        result = runner.invoke(cli, ["write", "--path", SOME_CI_SECRET_PATH, "--value", SOME_SECRET_VALUE,
                                     "--config_path", self.config_path])

        # then
        self.assertIs(0, result.exit_code, result.exception)

        self.vault_mock.verify_client_login("https://development", SOME_TOKEN_FOR_NONLIVE)
        self.vault_mock.verify_vault_write(SOME_CI_SECRET_PATH, SOME_SECRET_VALUE)

    def test_write_with_nonlive_label(self):
        # given
        self.vault_mock.set_write(SOME_CI_SECRET_PATH, SOME_SECRET_VALUE)
        self.vault_mock.set_write(SOME_DEVELOP_SECRET_PATH, SOME_SECRET_VALUE)

        # when
        runner = CliRunner()
        result = runner.invoke(cli, ["write", "--path", SOME_NONLIVE_SECRET_PATH, "--value", SOME_SECRET_VALUE,
                                     "--config_path", self.config_path])

        # then
        self.assertIs(0, result.exit_code, result.exception)

        self.vault_mock.verify_client_login("https://development", SOME_TOKEN_FOR_NONLIVE)
        self.vault_mock.verify_vault_write(SOME_CI_SECRET_PATH, SOME_SECRET_VALUE)
        self.vault_mock.verify_vault_write(SOME_DEVELOP_SECRET_PATH, SOME_SECRET_VALUE)

    def test_delete(self):
        # given
        self.vault_mock.set_delete(SOME_CI_SECRET_PATH)

        # when
        runner = CliRunner()
        result = runner.invoke(cli, ["delete", "--path", SOME_CI_SECRET_PATH,
                                     "--config_path", self.config_path])

        # then
        self.assertEquals(0, result.exit_code)
        self.vault_mock.verify_client_login("https://development", SOME_TOKEN_FOR_NONLIVE)
        self.vault_mock.verify_vault_delete(SOME_CI_SECRET_PATH)

    def test_delete_with_nonlive_label(self):
        # given
        self.vault_mock.set_delete(SOME_CI_SECRET_PATH)
        self.vault_mock.set_delete(SOME_DEVELOP_SECRET_PATH)

        # when
        runner = CliRunner()
        result = runner.invoke(cli, ["delete", "--path", SOME_NONLIVE_SECRET_PATH,
                                     "--config_path", self.config_path])

        # then
        self.assertEquals(0, result.exit_code)
        self.vault_mock.verify_client_login("https://development", SOME_TOKEN_FOR_NONLIVE)
        self.vault_mock.verify_vault_delete(SOME_CI_SECRET_PATH)
        self.vault_mock.verify_vault_delete(SOME_DEVELOP_SECRET_PATH)

    def test_read_policies(self):
        # given
        mesos_framework = "marathon"
        mesos_group = "myGroup"
        team = "myTeam"
        service = "myService"

        when(PolicyService).load_policies(mesos_framework, mesos_group, team, service) \
            .thenReturn({self._createPolicy(SOME_CI_SECRET_PATH)})

        # when
        runner = CliRunner()
        result = runner.invoke(cli,
                               ["read_policies",
                                "--mesos_framework", mesos_framework,
                                "--mesos_group", mesos_group,
                                "--microservice", "myTeam-myService",
                                "--config_path", self.config_path])

        # then
        self.assertEquals(0, result.exit_code)
        verify(PolicyService, times=1).load_policies(mesos_framework, mesos_group, team, service)
        self.assertIn(SOME_CI_SECRET_PATH, str(result.output))

    def test_add_policy(self):
        # given
        mesos_framework = "chronos"
        mesos_group = "myGroup"
        team = "myTeam"
        service = "myService"

        when(PolicyService).load_policies(mesos_framework, mesos_group, team, service).thenReturn(set())
        when(PolicyService).persist().thenReturn(None)

        # when
        runner = CliRunner()
        result = runner.invoke(cli, ["add_policies",
                                     "--mesos_framework", mesos_framework,
                                     "--mesos_group", mesos_group,
                                     "--microservice", "myTeam-myService",
                                     "--path", SOME_NONLIVE_SECRET_PATH,
                                     "--config_path", self.config_path])

        # then
        self.assertEquals(0, result.exit_code)
        verify(PolicyService, times=1).load_policies(mesos_framework, mesos_group, team, service)
        verify(PolicyService, times=1).persist()
        self.assertIn("ci/myTeam/myService/mongo.password", str(result.output))
        self.assertIn("develop/myTeam/myService/mongo.password", str(result.output))

    @staticmethod
    def _createPolicy(secret_path):
        return Policy({secret_path: {"policy": "read"}})
