import os
import unittest
from unittest import TestCase

from ddt import ddt, data, unpack

from vaultHelper.MyVaultConfiguration import MyVaultConfiguration


@ddt
class TestConfiguration(TestCase):
    def setUp(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        config_path = current_dir + "/.myVault/myVault.cfg"
        self.vault_config = MyVaultConfiguration(config_path)

    def test_get_policies_dir(self):
        # when
        dir = self.vault_config.get_policies_dir()
        # then
        self.assertEquals(dir, os.path.expanduser("~/policies"))

    def test_get_policies_template(self):
        # when
        template = self.vault_config.get_policies_template()
        # then
        self.assertEquals(template, "{mesos_framework}.{group}.{label}_{service}.{team}.{environment}.hcl")

    @data(("nonlive", "aliasForNonLive"),
          ("live", "live"))
    @unpack
    def test_get_alias_for_label(self, label, expected_alias):
        # when
        alias = self.vault_config.get_alias_for_label(label)
        # then
        self.assertEquals(alias, expected_alias)

    @data(("nonlive", ["ci", "develop"]),
          ("live", ["live"]))
    @unpack
    def test_get_environments(self, label, expected_environments):
        # when
        environments = self.vault_config.get_environments(label)
        # then
        self.assertEquals(environments, expected_environments)

    @data(("nonlive", "https://development"),
          ("live", "https://production"))
    @unpack
    def test_get_vault_endpoint(self, label, expected_endpoint):
        # when
        endpoint = self.vault_config.get_vault_endpoint(label)
        # then
        self.assertEquals(endpoint, expected_endpoint)

    @data(("ci", "nonlive"),
          ("develop", "nonlive"),
          ("develop/myteam/myservice/mysecret", "nonlive"),
          ("live", "live"),
          ("live/somepath", "live"))
    @unpack
    def test_get_label_for_path(self, environment, expected_label):
        # when
        label = self.vault_config.get_label_for_path(environment)
        # then
        self.assertEquals(label, expected_label)

    @unittest.expectedFailure
    def test_get_label_for_path_for_unknown_env(self):
        # given
        unknown_env = "unknown"
        # when
        self.vault_config.get_label_for_path(unknown_env)
        # then

    def test_get_labels(self):
        # when
        labels = self.vault_config.get_labels()
        # then
        self.assertEquals(labels, ["nonlive", "live"])
