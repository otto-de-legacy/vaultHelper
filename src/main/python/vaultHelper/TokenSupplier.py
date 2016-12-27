import json
import os

from os.path import expanduser


class TokenSupplier(object):
    DEFAULT_TOKEN_FILE_PATH = expanduser("~/.myvault/vaultTokens.json")

    def __init__(self, path=DEFAULT_TOKEN_FILE_PATH):
        self._file_path = path

    def persist(self, tokens):
        """
        :type tokens: json
        :rtype: None
        """
        fdesc = os.open(self._file_path, os.O_WRONLY | os.O_CREAT, 0o600)
        with open(fdesc, "w") as outfile:
            json.dump(tokens, outfile, indent=4)

    def read(self, label):
        """
        :type label: string
        :rtype: string
        """
        for token in self._read():
            if label in token.keys():
                return token[label]["VAULT_TOKEN"]

    def _read(self):
        """
        :rtype: json
        """
        return json.loads(open(self._file_path).read())
