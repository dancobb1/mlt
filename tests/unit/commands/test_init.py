#
# -*- coding: utf-8 -*-
#
# Copyright (c) 2018 Intel Corporation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# SPDX-License-Identifier: EPL-2.0
#
from __future__ import print_function

import os
import uuid
import shutil

import pytest

from mlt.commands.init import InitCommand
from test_utils import project
from test_utils.io import catch_stdout


@pytest.fixture
def checking_crds_mock(patch):
    return patch('kubernetes_helpers.checking_crds_on_k8')


@pytest.fixture
def open_mock(patch):
    return patch('open')


@pytest.fixture
def shutil_mock(patch):
    return patch('shutil')


@pytest.fixture
def process_helpers(patch):
    return patch('process_helpers')


@pytest.fixture
def check_output_mock(patch):
    return patch('check_output')


def test_init_dir_exists():
    new_dir = str(uuid.uuid4())
    os.mkdir(new_dir)
    init_dict = {
        'init': True,
        '--template': 'hello-world',
        '<name>': new_dir,
        '--skip-crd-check': True,
        '--template-repo': project.basedir()
    }
    try:
        with catch_stdout() as caught_output:
            with pytest.raises(SystemExit) as bad_init:
                InitCommand(init_dict).action()
                assert caught_output.getvalue() == \
                       "Directory '{}' already exists: delete ".format(
                           new_dir) + "before trying to initialize new " + \
                       "application"
                assert bad_init.value.code == 1
    finally:
        os.rmdir(new_dir)


def test_init(open_mock, process_helpers, shutil_mock, check_output_mock):
    check_output_mock.return_value.decode.return_value = 'bar'
    new_dir = str(uuid.uuid4())

    init_dict = {
        'init': True,
        '--template': 'hello-world',
        '--template-repo': project.basedir(),
        '--registry': None,
        '--namespace': None,
        '--skip-crd-check': True,
        '<name>': new_dir
    }
    init = InitCommand(init_dict)
    init.action()
    assert init.app_name == new_dir


def test_init_crd_check(checking_crds_mock, process_helpers, check_output_mock):
    new_dir = str(uuid.uuid4())
    init_dict = {
        'init': True,
        '--template': 'tf-distributed',
        '--template-repo': project.basedir(),
        '--registry': True,
        '--namespace': None,
        '--skip-crd-check': False,
        '<name>': new_dir
    }
    checking_crds_mock.return_value = {'tfjobs.kubeflow.org'}
    init = InitCommand(init_dict)
    try:
        with catch_stdout() as caught_output:
            init.action()
            output = caught_output.getvalue()

        message_code = output.find("tfjobs.kubeflow.org")
        assert message_code >= 0
    finally:
        shutil.rmtree(new_dir)
