import configparser
import os
import re
from configparser import ConfigParser


class MyVaultConfiguration(object):
    DEFAULT_CONFIGURATION_PATH = os.path.expanduser("~/.myvault/myVault.cfg")
    DEFAULT_MESOS_FRAMEWORK = "marathon"

    def __init__(self, path=DEFAULT_CONFIGURATION_PATH):
        self.config = ConfigParser()
        self.config.read(path)

    def get_policies_dir(self):
        return os.path.expanduser(self.config.get("globals", "policiesDir"))

    def get_policies_template(self):
        return self.config.get("globals", "policyNameTemplate")

    def get_environments(self, label):
        """
        :type label: string
        :rtype: list
        """
        env = self.config.get(label, "environments")
        return self._getlist(env)

    def get_alias_for_label(self, label):
        """
        :type label: string
        :rtype: string
        """
        try:
            return self.config.get(label, "alias")
        except configparser.NoOptionError:
            return label

    def get_label_for_path(self, path):
        """
        :type path: string
        :rtype: string
        """
        m = re.search('[/]?(\w+).*', path)
        if m is not None:
            prefix = m.group(1)
            for label in self.get_labels():
                if prefix in [label] + self.get_environments(label):
                    return label
        raise ValueError("unexpected environment %s" % path)

    def get_vault_endpoint(self, label):
        """
        :type label: string
        :rtype: string
        """
        return self.config.get(label, "serverAddress")

    def get_labels(self):
        """
        :rtype: list
        """
        return [x for x in self.config.sections() if x != "globals"]

    @staticmethod
    def _getlist(delimited_list_string, sep=',', chars=None):
        """
        :type delimited_list_string: string
        :rtype: list
        """
        """Return a list from a ConfigParser option. By default,
           split on a comma and strip whitespaces."""
        return [chunk.strip(chars) for chunk in delimited_list_string.split(sep)]
