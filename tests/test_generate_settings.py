# -*- coding: utf-8 -*-
import argparse
import os

import mock
import pytest
from six.moves import configparser

from django.core.management.base import CommandError

from django_settings_custom import encryption
from django_settings_custom.management.commands import generate_settings

resources_dir = os.path.join(os.path.dirname(__file__), "resources")
template_file_path = os.path.join(resources_dir, "conf_template_test.ini")
created_file_path = os.path.join(resources_dir, "conf_test.ini")
if os.path.exists(created_file_path):
    os.remove(created_file_path)


class FakeSettings:
    configured = True
    DEBUG = False
    SECRET_KEY = "$lj&)_)1cc7tm3qikje-u*45mz8za^0wuf*^pm0qjs=xcwy=vo"

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)


def init_and_launch_command(command_arguments, command_class=generate_settings.Command):
    parser = argparse.ArgumentParser()
    c = command_class()
    c.add_arguments(parser)
    options = parser.parse_args(command_arguments)
    cmd_options = vars(options)
    # Move positional args out of options to mimic legacy optparse
    args = cmd_options.pop("args", ())
    c.handle(*args, **cmd_options)


@mock.patch("getpass.getpass")
@mock.patch("django_settings_custom.management.commands.generate_settings.get_input")
@mock.patch("django.conf.settings", FakeSettings())
def test_error_missing_template_path(input_mock, getpass_mock):
    input_mock.side_effect = ["y", "y", "user"]
    getpass_mock.return_value = "pass"

    with pytest.raises(CommandError):
        init_and_launch_command([])


@mock.patch("getpass.getpass")
@mock.patch("django_settings_custom.management.commands.generate_settings.get_input")
@mock.patch(
    "django.conf.settings", FakeSettings(SETTINGS_TEMPLATE_FILE=template_file_path)
)
def test_error_missing_file_path(input_mock, getpass_mock):
    input_mock.side_effect = ["y", "y", "user"]
    getpass_mock.return_value = "pass"
    with pytest.raises(CommandError):
        init_and_launch_command([])


@mock.patch("getpass.getpass")
@mock.patch("django_settings_custom.management.commands.generate_settings.get_input")
@mock.patch(
    "django.conf.settings",
    FakeSettings(
        SETTINGS_TEMPLATE_FILE="path/not/existing.ini",
        SETTINGS_FILE_PATH=created_file_path,
    ),
)
def test_error_wrong_path(input_mock, getpass_mock):
    input_mock.side_effect = ["y", "user"]
    getpass_mock.return_value = "pass"
    with pytest.raises(CommandError):
        init_and_launch_command([])


@mock.patch("getpass.getpass")
@mock.patch("django_settings_custom.management.commands.generate_settings.get_input")
@mock.patch(
    "django.conf.settings",
    FakeSettings(
        SETTINGS_TEMPLATE_FILE=template_file_path, SETTINGS_FILE_PATH=created_file_path
    ),
)
def test_generate_file(input_mock, getpass_mock):
    input_mock.side_effect = ["y", "user"]
    getpass_mock.return_value = "pass"
    init_and_launch_command([])
    assert os.path.exists(created_file_path)
    os.remove(created_file_path)


@mock.patch("getpass.getpass")
@mock.patch("django_settings_custom.management.commands.generate_settings.get_input")
@mock.patch(
    "django.conf.settings",
    FakeSettings(
        SETTINGS_TEMPLATE_FILE=template_file_path, SETTINGS_FILE_PATH=created_file_path
    ),
)
def test_generate_file_override(input_mock, getpass_mock):
    f = open(created_file_path, "w")
    f.write("An existing settings file")
    f.close()
    input_mock.side_effect = ["y", "y", "user"]
    getpass_mock.return_value = "pass"

    init_and_launch_command([])
    assert os.path.exists(created_file_path)
    os.remove(created_file_path)


@mock.patch("django_settings_custom.management.commands.generate_settings.get_input")
@mock.patch(
    "django.conf.settings",
    FakeSettings(
        SETTINGS_TEMPLATE_FILE=template_file_path, SETTINGS_FILE_PATH=created_file_path
    ),
)
def test_cancel_generate_file_override(input_mock):
    f = open(created_file_path, "w")
    f.write("An existing settings file")
    f.close()
    input_mock.side_effect = ["n"]

    with pytest.raises(CommandError):
        init_and_launch_command([])
    os.remove(created_file_path)


@mock.patch("getpass.getpass")
@mock.patch("django_settings_custom.management.commands.generate_settings.get_input")
@mock.patch(
    "django.conf.settings",
    FakeSettings(
        SETTINGS_TEMPLATE_FILE=template_file_path, SETTINGS_FILE_PATH=created_file_path
    ),
)
def test_error_generate_file_with_secretkey_entered(input_mock, getpass_mock):
    input_mock.side_effect = ["n", ""]
    with pytest.raises(CommandError):
        init_and_launch_command([])


@mock.patch("getpass.getpass")
@mock.patch("django_settings_custom.management.commands.generate_settings.get_input")
@mock.patch(
    "django.conf.settings",
    FakeSettings(
        SETTINGS_TEMPLATE_FILE=template_file_path, SETTINGS_FILE_PATH=created_file_path
    ),
)
def test_generate_file_with_secretkey_entered(input_mock, getpass_mock):
    input_mock.side_effect = ["n", FakeSettings.SECRET_KEY, "user"]
    getpass_mock.return_value = "pass"
    init_and_launch_command([])
    assert os.path.exists(created_file_path)

    config = configparser.ConfigParser()
    config.read(created_file_path)

    secret_key = config.get("DJANGO", "KEY")
    assert secret_key == FakeSettings.SECRET_KEY
    assert config.get("DATABASE_CREDENTIALS", "USER") == "user"
    assert (
        encryption.decrypt(config.get("DATABASE_CREDENTIALS", "PASSWORD"), secret_key)
        == "pass"
    )

    os.remove(created_file_path)


@mock.patch("getpass.getpass")
@mock.patch("django_settings_custom.management.commands.generate_settings.get_input")
@mock.patch("django.conf.settings", FakeSettings())
def test_generate_file_command_args(input_mock, getpass_mock):
    input_mock.side_effect = ["user"]
    getpass_mock.return_value = "pass"
    init_and_launch_command([template_file_path, created_file_path, "--force-secretkey"])
    assert os.path.exists(created_file_path)
    os.remove(created_file_path)


@mock.patch("getpass.getpass")
@mock.patch("django_settings_custom.management.commands.generate_settings.get_input")
@mock.patch("django.conf.settings", FakeSettings())
def test_generate_file_with_subclass(input_mock, getpass_mock):

    class CustomCommand(generate_settings.Command):

        settings_template_file = template_file_path
        settings_file_path = created_file_path
        force_secret_key = True

    input_mock.side_effect = ["user"]
    getpass_mock.return_value = "pass"
    init_and_launch_command([], CustomCommand)
    assert os.path.exists(created_file_path)
    os.remove(created_file_path)
