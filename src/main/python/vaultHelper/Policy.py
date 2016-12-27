import re


class Policy(object):
    def __init__(self, json):
        """
        @type json: dict
        """
        self.path = str(list(json.keys())[0])
        self.policy = str(json.get(self.path).get("policy"))

    def get_env(self):
        """
        :rtype string
        """
        match = re.match(r"([^/]*)", self.path)

        if match:
            return match.group(1)

        return None

    def __str__(self):
        return "path \"%s\" {\n\tpolicy = \"%s\"\n}\n" % (self.path, self.policy)

    def __eq__(self, other):
        return self.path == other.path and self.policy == other.policy

    def __hash__(self):
        return hash((self.path, self.policy))
