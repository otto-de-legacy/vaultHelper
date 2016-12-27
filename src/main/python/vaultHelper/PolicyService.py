import os
import re
from itertools import groupby

from hcl import api
from vaultHelper.Policy import Policy


class PolicyService(object):
    def __init__(self, vault_config):
        """
        :type vault_config: MyVaultConfiguration
        """
        self._policy_dir = vault_config.get_policies_dir()
        self._policy_template = vault_config.get_policies_template()
        self._vault_config = vault_config
        self._mesos_framework = None
        self._mesos_group = None
        self._team = None
        self._service = None
        self._policies = set()

    def load_policies(self, mesos_framework, mesos_group, team, service):
        """
        :type mesos_framework: string
        :type mesos_group: string
        :type team: string
        :type service: string
        :rtype: list
        """
        self._policies = set()
        self._mesos_framework = mesos_framework
        self._mesos_group = mesos_group
        self._team = team
        self._service = service

        regular_expression = self._policy_template.replace(".", "\.").format(
            mesos_framework=self._mesos_framework,
            group=self._mesos_group, team=self._team,
            service=self._service, environment=".*",
            label=".*")

        files = [self._policy_dir + "/" + f for f in os.listdir(self._policy_dir) if re.match(regular_expression, f)]
        for f in files:
            file = open(f, 'r')
            hcl = api.load(file).get("path")
            for key in hcl.keys():
                self._policies.add(Policy({key: hcl.get(key)}))
        return self._sorted_policies()

    def add_read_policy(self, secret_path):
        """
        :type secret_path: string
        """
        self._policies.add(Policy({self._normalize_path(secret_path): {"policy": "read"}}))

    def get_policies(self):
        """
        :rtype: list
        """
        return self._sorted_policies()

    def persist(self):
        if self._mesos_group is None:
            raise Exception("should load policies first")

        sorted_policies = self._sorted_policies()

        for env, policies in groupby(sorted_policies, key=lambda policy: policy.get_env()):
            label = self._vault_config.get_label_for_path(env)
            filename = self._policy_template.format(
                mesos_framework=self._mesos_framework,
                group=self._mesos_group, team=self._team, service=self._service, environment=env,
                label=self._vault_config.get_alias_for_label(label)
            )
            file = open(self._policy_dir + "/" + filename, "w")
            for p in policies:
                file.write(str(p))
            file.close()

    def _sorted_policies(self):
        """
        :rtype: list
        """
        return sorted(self._policies, key=lambda policy: policy.path)

    @staticmethod
    def _normalize_path(path):
        """
        :type path: string
        :rtype: string
        """
        match = re.match(r"/?(.*)", path)
        if match:
            return match.group(1)

        return None
