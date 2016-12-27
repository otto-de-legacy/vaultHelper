from unittest import TestCase

from ddt import data, ddt
from vaultHelper.Policy import Policy


@ddt
class TestPolicy(TestCase):
    def test_str(self):
        # given
        json = {"develop/myTeam/myService/someSecret": {"policy": "read"}}
        # when
        policy = Policy(json)
        # then
        self.assertEquals("path \"develop/myTeam/myService/someSecret\" {\n\tpolicy = \"read\"\n}\n",
                          policy.__str__())

    @data("ci", "develop", "live")
    def test_get_env(self, environment):
        # given
        policy = Policy({environment + "/myTeam/myService/someSecret": {"policy": "read"}})

        # then
        self.assertEquals(environment, policy.get_env())
