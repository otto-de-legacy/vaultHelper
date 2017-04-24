#  vaultHelper
#  Copyright 2016. José Mejía otto.de
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

"""
https://github.com/otto-de/vaultHelper
-----
The vaultHelper is a command-line utility written in python for managing easily vault secrets and policies in an easy manner.

Links
`````
* vaultHelper Github repository <https://github.com/otto-de/vaultHelper>
"""

from pybuilder.core import use_plugin, init, Author

use_plugin("python.core")
use_plugin("python.unittest")
use_plugin("python.install_dependencies")
use_plugin("python.flake8")
use_plugin("python.distutils")
use_plugin("python.pycharm")
use_plugin("copy_resources")

name = "vaultHelper"
default_task = ["clean", "analyze", "publish"]

version = "1.1.0"
summary = "Command-line utility for vault secrets and policies management"
description = __doc__
authors = (Author("José Mejía", "jose.mejia@otto.de"),)
url = "https://github.com/otto-de/vaultHelper"
license = "Apache Software License"
include_package_data = True

@init
def set_properties(project):
    project.set_property("verbose", True)
    project.build_depends_on("hvac")
    project.build_depends_on("requests")
    project.build_depends_on("pyhcl")
    project.build_depends_on("colorama")
    project.build_depends_on("click")
    project.build_depends_on("mockito")
    project.build_depends_on("ddt")
    project.set_property('unittest_module_glob', 'test_*')
    project.set_property('dir_dist', 'distribution')

    project.build_depends_on_requirements("requirements-dev.txt")
    project.depends_on_requirements("requirements.txt")
    project.set_property("copy_resources_target", '$dir_dist')
    project.get_property("copy_resources_glob").append("setup.cfg")
