
# vaultHelper

The *vaultHelper* is a command line tool written in python to manage vault secrets and policies
in an easy manner.

## Introduction

Vault is a tool for managing a secret store which comprises passwords, tokens, certificates, keys,
and their access policies as well.  Since a developer team is usually provided with different staging environments and
vault endpoints, the cost of the vault secret management increases terribly.  

The *vaultHelper* eases this process by mapping staging environments and vault endpoints to
**labels** like *nonlive* and *live*.  This allows logging-in to all vault endpoints at once
and preserving the tokens for the next commands, provided that your LDAP user is the same.  The labels let you write secrets faster for several environments and set their read policies with only one command.

The *vaultHelper* has been developed in *Python 3.5.2 :: Anaconda 4.2.0 (64-bit)* under *Xubuntu 16.10*.  Porting this tool to unlike systems might demand some effort.

## How to install it?

*vaultHelper* can be installed with `pip` from the  tarball located in the distribution folder of this repository.

```bash
$ pip install vaultHelper-x.x.x.tar.gz --trusted-host pypi.python.org
```

Create the directory *~/.myvault*

```bash
$ mkdir ~/.myvault
$ chmod 700 ~/.myvault
```

Concatenate the required SSL certificates into the file *~/.myvault/ca.bundle*

Finally, provide the configuration file *~/.myvault/myVault.cfg* based on the following example, where each section except *globals* is considered a *label*.

```
[nonlive]
serverAddress = https://development
environments = ci, develop
alias = aliasForNonLive

[live]
serverAddress = https://production
environments = live

[globals]
#git working directory for vault policies
policiesDir = ~/policies
policyNameTemplate = {mesos_framework}.{group}.{label}_{service}.{team}.{environment}.hcl
```

After the successful installation, the command *myvault.py* should be available in your path:

```bash
$ which myvault.py
/usr/local/dev/anaconda3/bin/myvault.py
```

## How to use it?

When executed without parameters, *myvault.py* will show its available commands.

```bash
$ myvault.py

Usage: myvault.py [OPTIONS] COMMAND [ARGS]...

Options:
  --help  Show this message and exit.

Commands:
  add_policies
  delete
  list
  login
  read
  read_policies
  write
```

Some help is displayed when using the *--help* argument behind any command.

```bash
$ myvault.py read --help
Usage: myvault.py read [OPTIONS]

Options:
  --path TEXT         Secret path, e.g. env/myTeam/myService/jdbc.password
  --config_path TEXT
  --help              Show this message and exit.
```


Whenever you call *myvault.py* with a command, it will prompt for the required arguments.

First, authenticate against all vault endpoints at once with your LDAP credentials via the *login* command.  As a result, you will obtain one token per label. The *vaultHelper* will choose the right token for the read, list, write, and delete commands according
to the environment of the secret path.

```bash
$ myvault.py login
Ldapusername: jose
Ldappassword:
> Got token xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx for nonlive
> Got token yyyyyyyy-yyyy-yyyy-yyyy-yyyyyyyyyyyy for live
```

By using the command *read*, it is possible to access the secret value for a single environment.

```bash
jmejia@portobelo:~/otto/myvault$ myvault.py read
Path: ci/myTeam/myService/jdbc.password
> path=ci/myTeam/myService/jdbc.password, value=somePassword
```

When employing a label instead of an environment in the secret path, you can read the secrets
corresponding to all the environments in the label.

```bash
$ myvault.py read
Path: nonlive/myTeam/myService/jdbc.password
> path=ci/myTeam/myService/jdbc.password, value=somePassword
> path=develop/myTeam/myService/jdbc.password, value=somePassword
```

The same applies to the *list* command as well.

```bash
$ myvault.py list
Path: nonlive/opal/brand
> ci/opal/brand has 1 value(s):
>	  ci/myTeam/myService
> develop/opal/brand has 1 value(s):
>   develop/myTeam/myService

```


Additionally, the label-to-environments mapping allows you to write or delete the same secret value for all environments sharing a label at once.

```bash
$ myvault.py write
Path: nonlive/myTeam/myService/mongo.password
Value: testing
> writing ci/myTeam/myService/mongo.password
> writing develop/myTeam/myService/mongo.password
```

*vaultHelper* can only add read policies to the git working directory provided in the *myVault.cfg* file.  It is strongly recommended to review the changes yourself (git diff) before pushing them.

Remind that some files might be modified since *vaultHelper* sorts the secret paths alphabetically.

If a label is provided of an alias, it will be used to determine the corresponding hcl filename.

```bash
$ myvault.py add_policies
Mesos group: mesosGroup
Microservice, e.g., myTeam-myService: myTeam-myService
Secret path, e.g. env/myTeam/myService/jdbc.password: nonlive/myTeam/myService/jdbc.password
>	develop-ci/myTeam/myService/jdbc.password
>	develop/myTeam/myService/jdbc.password
>	fit/myTeam/myService/jdbc.password
>	prelive/myTeam/myService/jdbc.password
```


## Release Notes

### Version 1.00 released 2016-12-27
* Initial release

## License
vaultHelper is published under the terms of the [Apache License, Version 2](http://www.apache.org/licenses/LICENSE-2.0.html).

## Additional Links
* [vault](https://www.vaultproject.io/)
* [anaconda Downloads](https://www.continuum.io/downloads)
