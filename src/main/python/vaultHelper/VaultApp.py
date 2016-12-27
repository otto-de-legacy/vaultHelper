import re

import click

from vaultHelper.MyVaultConfiguration import MyVaultConfiguration
from vaultHelper.PolicyService import PolicyService
from vaultHelper.TokenSupplier import TokenSupplier
from vaultHelper.VaultService import VaultService

VAULT_TOKEN = 'VAULT_TOKEN'


@click.group()
def cli():
    pass


@cli.command()
@click.option('--ldapusername', prompt=True, help="LDAP username")
@click.option('--ldappassword', prompt=True, hide_input=True, help="LDAP password")
@click.option('--config_path', default=MyVaultConfiguration.DEFAULT_CONFIGURATION_PATH, help="Optional")
def login(ldapusername, ldappassword, config_path):
    """
    :type ldapusername: string
    :type ldappassword: string
    :type config_path: string
    """
    vault_service = VaultService()
    configuration = MyVaultConfiguration(config_path)
    token_supplier = TokenSupplier()
    tokens = []
    for label in configuration.get_labels():
        server_address = configuration.get_vault_endpoint(label)
        client = vault_service.login_with_ldap(server_address, ldapusername, ldappassword)
        tokens.append({label: {
            VAULT_TOKEN: client.token,
        }})
        click.secho("Got token %s for %s" % (client.token, label), fg="green")
    token_supplier.persist(tokens)


@cli.command()
@click.option('--path', prompt=True, help="Secret path, e.g. env/myTeam/myService/jdbc.password")
@click.option('--config_path', default=MyVaultConfiguration.DEFAULT_CONFIGURATION_PATH, help="Optional")
def read(path, config_path):
    """
    :type path: string
    :type config_path: string
    """
    vault_service = VaultService()
    configuration = MyVaultConfiguration(config_path)
    label = configuration.get_label_for_path(path)

    _login_with_token(configuration, label, vault_service)

    paths = _expand_paths(configuration, label, path)

    for currentPath in paths:
        click.secho("path=%s, value=%s" % (currentPath, vault_service.read(currentPath)), fg="green")


@cli.command()
@click.option('--path', prompt=True, help="Secret path, e.g. env/myTeam/myService")
@click.option('--config_path', default=MyVaultConfiguration.DEFAULT_CONFIGURATION_PATH, help="Optional")
def list(path, config_path):
    """
    :type path: string
    :type config_path: string
    """
    vault_service = VaultService()
    configuration = MyVaultConfiguration(config_path)
    label = configuration.get_label_for_path(path)
    _login_with_token(configuration, label, vault_service)

    paths = _expand_paths(configuration, label, path)

    for currentPath in paths:
        values = vault_service.list(currentPath)
        if values:
            click.echo("%s has %i value(s):" % (currentPath, len(values)))
            for i in values:
                click.secho("\t%s" % i, fg="green")
        else:
            click.echo("%s has no match" % currentPath)


@cli.command()
@click.option('--path', prompt=True, help="Secret path, e.g. env/myTeam/myService/jdbc.password")
@click.option('--value', prompt=True, help="Secret value")
@click.option('--config_path', default=MyVaultConfiguration.DEFAULT_CONFIGURATION_PATH, help="Optional")
def write(path, value, config_path):
    """
    :type path: string
    :type value: string
    :type config_path: string
    """
    vault_service = VaultService()
    configuration = MyVaultConfiguration(config_path)
    label = configuration.get_label_for_path(path)
    _login_with_token(configuration, label, vault_service)

    paths = _expand_paths(configuration, label, path)
    for currentPath in paths:
        click.secho("writing %s" % currentPath, fg="green")
        vault_service.write(currentPath, value)


@cli.command()
@click.option('--path', prompt=True, help="Secret path, e.g. env/myTeam/myService/jdbc.password")
@click.option('--config_path', default=MyVaultConfiguration.DEFAULT_CONFIGURATION_PATH, help="Optional")
def delete(path, config_path):
    """
    :type path: string
    :type config_path: string
    """
    vault_service = VaultService()
    configuration = MyVaultConfiguration(config_path)
    label = configuration.get_label_for_path(path)

    _login_with_token(configuration, label, vault_service)

    paths = _expand_paths(configuration, label, path)
    for currentPath in paths:
        click.secho("deleting %s" % currentPath, fg="green")
        vault_service.delete(currentPath)


@cli.command()
@click.option('--mesos_framework', default=MyVaultConfiguration.DEFAULT_MESOS_FRAMEWORK,
              help="mesos framework, e.g., marathon|chronos")
@click.option('--mesos_group', prompt=True, help="organizational mesos group")
@click.option('--microservice', prompt="Microservice, e.g. myTeam-myService", help="myTeam-myService")
@click.option('--config_path', default=MyVaultConfiguration.DEFAULT_CONFIGURATION_PATH, help="Optional")
def read_policies(mesos_framework, mesos_group, microservice, config_path):
    """
    :type mesos_framework: string
    :type mesos_group: string
    :type microservice: string
    :type config_path: string
    """
    configuration = MyVaultConfiguration(config_path)
    policy_service = PolicyService(configuration)
    (team, service) = _extract_team_and_service(microservice)
    policies = policy_service.load_policies(mesos_framework, mesos_group, team, service)
    for policy in policies:
        click.secho("\t%s" % policy.path, fg="green")


@cli.command()
@click.option('--mesos_framework', default=MyVaultConfiguration.DEFAULT_MESOS_FRAMEWORK,
              help="mesos framework, e.g., marathon|chronos")
@click.option('--mesos_group', prompt=True, help="organizational mesos group")
@click.option('--microservice', prompt="Microservice, e.g., myTeam-myService", help="myTeam-myService")
@click.option('--path', prompt="Secret path, e.g. env/myTeam/myService/jdbc.password",
              help="Secret path, e.g. env/myTeam/myService/jdbc.password")
@click.option('--config_path', default=MyVaultConfiguration.DEFAULT_CONFIGURATION_PATH, help="Optional")
def add_policies(mesos_framework, mesos_group, microservice, path, config_path):
    """
    :type mesos_framework: string
    :type mesos_group: string
    :type microservice: string
    :type path: string
    :type config_path: string
    """
    configuration = MyVaultConfiguration(config_path)
    policy_service = PolicyService(configuration)
    (team, service) = _extract_team_and_service(microservice)
    policy_service.load_policies(mesos_framework, mesos_group, team, service)

    label = configuration.get_label_for_path(path)
    paths = _expand_paths(configuration, label, path)
    for currentPath in paths:
        policy_service.add_read_policy(currentPath)

    policy_service.persist()

    for policy in policy_service.get_policies():
        click.secho("\t%s" % policy.path, fg="green")


def _get_token_credentials(label):
    """
    :type label: string
    :rtype: string
    """
    return TokenSupplier().read(label)


def _expand_paths(configuration, label, path):
    """
    :type configuration: MyVaultConfiguration
    :type label: string
    :type path: string
    :rtype: list
    """
    match = re.match(r"(%s)(/.*)" % label, path)

    if match:
        paths = [env + match.group(2) for env in configuration.get_environments(label)]
    else:
        paths = [path]
    return paths


def _login_with_token(configuration, label, service):
    """
    :type configuration: MyVaultConfiguration
    :type label: string
    :type service: VaultService
    :rtype: None
    """
    vault_address = configuration.get_vault_endpoint(label)
    vault_token = _get_token_credentials(label)
    service.login_with_token(vault_address, vault_token)


def _extract_team_and_service(microservice):
    """
    :type microservice: string
    :rtype: list
    """
    match = re.match(r'([^-]*)-(.*)', microservice)
    if match:
        return [match.group(1), match.group(2)]
    raise Exception("invalid microservice value")


if __name__ == '__main__':
    cli()
