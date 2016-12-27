import os
import shutil
from unittest import TestCase

from ddt import ddt, data, unpack
from hamcrest import assert_that, contains_inanyorder

from vaultHelper.MyVaultConfiguration import MyVaultConfiguration
from vaultHelper.Policy import Policy
from vaultHelper.PolicyService import PolicyService


@ddt
class TestPolicyService(TestCase):
    def setUp(self):
        self.current_dir = os.path.dirname(os.path.abspath(__file__))
        config_path = self.current_dir + "/.myVault/myVault.cfg"
        self.vault_config = MyVaultConfiguration(config_path)

        target_dir = self.current_dir + "/out"
        shutil.rmtree(target_dir, True)
        os.mkdir(target_dir)

    def test_load_policies(self):
        # given
        service = PolicyService(self.vault_config)
        service._policy_dir = self.current_dir + "/policies"
        # when
        service.load_policies("marathon", "myGroup", "myTeam", "myService")
        # then
        self.assertEquals(6, len(service._policies))
        self.assertEquals("marathon", service._mesos_framework)
        self.assertEquals("myGroup", service._mesos_group)
        self.assertEquals("myTeam", service._team)
        self.assertEquals("myService", service._service)

        expected_policies = self.expected_policies()
        for policy in service._policies:
            self.assertIn(policy, expected_policies)

    def test_add_read_policy(self):
        # given
        secret_path = "develop/myTeam/myService/someSecret"
        service = PolicyService(self.vault_config)
        service._policy_dir = self.current_dir + "/out"

        # when
        service.add_read_policy(secret_path)
        # then
        self.assertEquals([self._create_policy(secret_path)], list(service._policies))

    def test_persist(self):
        # given
        target_dir = self.current_dir + "/out"

        service = PolicyService(self.vault_config)
        service._policy_dir = target_dir
        service._mesos_framework = "marathon"
        service._mesos_group = "myGroup"
        service._service = "myService"
        service._team = "myTeam"

        service._policies = set()
        service._policies.add(self._create_policy("ci/myTeam/myService/mongo.password"))
        service._policies.add(self._create_policy("develop/myTeam/myService/mongo.password"))
        service._policies.add(self._create_policy("live/myTeam/myService/mongo.password"))
        service._policies.add(self._create_policy("live/myTeam/myService/jdbc.password"))
        # when
        service.persist()

        # then
        files = [f for f in os.listdir(target_dir)]
        assert_that(files, contains_inanyorder("marathon.myGroup.live_myService.myTeam.live.hcl",
                                               "marathon.myGroup.aliasForNonLive_myService.myTeam.ci.hcl",
                                               "marathon.myGroup.aliasForNonLive_myService.myTeam.develop.hcl"))

    @data(("ci/myTeam/myService/mongo.password", "ci/myTeam/myService/mongo.password"),
          ("/ci/myTeam/myService/mongo.password", "ci/myTeam/myService/mongo.password"))
    @unpack
    def test_normalize_path(self, path, expected_normalized_path):
        # given
        service = PolicyService(self.vault_config)
        # when
        normalized_path = service._normalize_path(path)

        # then
        self.assertEquals(expected_normalized_path, normalized_path)

    def expected_policies(self):
        return [self._create_policy("live/myTeam/myService/mongo.password"),
                self._create_policy("live/myTeam/myService/jdbc.password"),
                self._create_policy("ci/myTeam/myService/mongo.password"),
                self._create_policy("ci/myTeam/myService/jdbc.password"),
                self._create_policy("develop/myTeam/myService/mongo.password"),
                self._create_policy("develop/myTeam/myService/jdbc.password")
                ]

    @staticmethod
    def _create_policy(secret_path):
        return Policy({secret_path: {"policy": "read"}})
