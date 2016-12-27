from os.path import expanduser

import hvac
from requests.packages import urllib3

DEFAULT_CERT_BUNDLE_FILE_PATH = expanduser("~/.myvault/ca.bundle")


class VaultService(object):
    def __init__(self, certbundlePath=DEFAULT_CERT_BUNDLE_FILE_PATH):
        urllib3.disable_warnings()
        self._client = None
        self._certbundle_file_path = certbundlePath

    def login(self, **kwargs):
        """
        :type kwargs: dict
        :rtype: hvac.v1.Client
        """
        kwargs['verify'] = self._certbundle_file_path
        self._client = hvac.Client(kwargs)
        return self._client

    def login_with_ldap(self, vaultaddress, ldapusername, ldappasswd):
        """
        :rtype: hvac.v1.Client
        """
        args = {"url": vaultaddress, "verify": self._certbundle_file_path}
        self._client = hvac.Client(**args)
        self._client.auth_ldap(ldapusername, ldappasswd)
        return self._client

    def login_with_token(self, vaultaddress, token):
        """
        :rtype: hvac.v1.Client
        """
        args = {"url": vaultaddress, "token": token, "verify": self._certbundle_file_path}
        self._client = hvac.Client(**args)
        return self._client

    def read(self, path):
        """
        :type path: string
        :rtype: string
        """
        result = self._client.read(path)
        if result is None:
            return
        return result.get("data").get("value")

    def list(self, path):
        """
        :type path: string
        :rtype: list
        """
        result = self._client.list(path)
        if result is None:
            return
        return result.get("data").get("keys")

    def write(self, path, value):
        """
        :type path: string
        :type value: string
        :rtype: None
        """
        self._client.write(path, value=value)

    def delete(self, path):
        """
        :type path: string
        :rtype: None
        """
        self._client.delete(path)
