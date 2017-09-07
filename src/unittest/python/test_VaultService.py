from unittest import TestCase

import hvac
import os
from mockito import when, matchers, mock, verify, unstub
from vaultHelper.VaultService import VaultService


class TestVaultService(TestCase):
    BASE_PATH = "/home/someUser"
    CA_BUNDLE_PATH = BASE_PATH + "/ca/ca.bundle"

    def setUp(self):
        when(os.path).dirname(matchers.any(object)).thenReturn(TestVaultService.BASE_PATH)

    def tearDown(self):
        unstub()

    def test_loginwithldap(self):
        # given
        client_mock = mock(hvac.Client)
        vault_addr = "someVaultAddress"
        username = "someUser"
        passwd = "somePasswd"

        service = VaultService(TestVaultService.CA_BUNDLE_PATH)

        when(hvac).Client(**{"url": vault_addr, "verify": TestVaultService.CA_BUNDLE_PATH}).thenReturn(
            client_mock)
        when(client_mock).auth_ldap(matchers.any(str), matchers.any(str))

        # when
        result = service.login_with_ldap(vault_addr, username, passwd)

        # then
        self.assertEquals(client_mock, result)
        verify(hvac, times=1).Client(**{"url": vault_addr, "verify": TestVaultService.BASE_PATH + "/ca/ca.bundle"})
        verify(client_mock, times=1).auth_ldap(username, passwd)

    def test_loginwithtoken(self):
        # given
        client_mock = mock(hvac.Client)
        vault_addr = "someVaultAddress"
        token = "someToken"

        service = VaultService(TestVaultService.CA_BUNDLE_PATH)

        when(hvac).Client(
            **{"url": vault_addr, "token": token, "verify": TestVaultService.CA_BUNDLE_PATH}).thenReturn(
            client_mock)

        # when
        result = service.login_with_token(vault_addr, token)

        # then
        self.assertEquals(client_mock, result)
        verify(hvac, times=1).Client(
            **{"url": vault_addr, "token": token, "verify": TestVaultService.CA_BUNDLE_PATH})

    def test_read(self):
        # given
        path = "somePath"
        client_mock = mock(hvac.Client)

        when(client_mock).read(path).thenReturn({"data": {"value": "Hello World"}})

        service = VaultService()
        service._client = client_mock

        # when
        result = service.read(path)

        # then
        self.assertEquals("Hello World", result)

    def test_list(self):
        # given
        path = "somePath"
        client_mock = mock(hvac.Client)

        when(client_mock).list(path).thenReturn({"data": {"keys": ["secret1", "secret2"]}})

        service = VaultService()
        service._client = client_mock

        # when
        result = service.list(path)

        # then
        self.assertEquals(["secret1", "secret2"], result)

    def test_write(self):
        # given
        path = "somePath"
        somevalue = "someValue"
        client_mock = mock(hvac.Client)

        when(client_mock).write(path, **{"value": somevalue})

        service = VaultService()
        service._client = client_mock

        # when
        service.write(path, somevalue)

        # then
        verify(client_mock, times=1).write(path, **{"value": somevalue})

    def test_delete(self):
        # given
        path = "somePath"
        client_mock = mock(hvac.Client)

        when(client_mock).delete(path).thenReturn(None)

        service = VaultService()
        service._client = client_mock

        # when
        service.delete(path)

        # then
        verify(client_mock, times=1).delete(path)
