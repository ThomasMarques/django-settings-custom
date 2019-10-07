# -*- coding: utf-8 -*-
"""Test generation settings file."""
import argparse
import os

import pytest
from six.moves import configparser

from django.core.management.base import CommandError

from django_settings_custom import encryption
from django_settings_custom.management.commands import generate_settings

try:
    from unittest import mock
except ImportError:
    import mock

RESOURCES_DIR = os.path.join(os.path.dirname(__file__), "resources")
TEMPLATE_FILE_PATH = os.path.join(RESOURCES_DIR, "conf_template_test.ini")
CREATED_FILE_PATH = os.path.join(RESOURCES_DIR, "conf_test.ini")
if os.path.exists(CREATED_FILE_PATH):
    os.remove(CREATED_FILE_PATH)


class FakeSettings:
    """Class to mock django settings."""

    configured = True
    DEBUG = False
    SECRET_KEY = "$lj&)_)1cc7tm3qikje-u*45mz8za^0wuf*^pm0qjs=xcwy=vo"

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)


def init_and_launch_command(command_arguments, command_class=generate_settings.Command):
    """Launch file generation as command."""
    parser = argparse.ArgumentParser()
    command = command_class()
    command.add_arguments(parser)
    options = parser.parse_args(command_arguments)
    cmd_options = vars(options)
    # Move positional args out of options to mimic legacy optparse
    args = cmd_options.pop("args", ())
    command.handle(*args, **cmd_options)


@mock.patch("getpass.getpass")
@mock.patch("django_settings_custom.management.commands.generate_settings.get_input")
@mock.patch("django.conf.settings", FakeSettings())
def test_error_missing_template_path(input_mock, getpass_mock):
    """Test missing template"""
    input_mock.side_effect = ["y", "y", "user"]
    getpass_mock.return_value = "pass"

    with pytest.raises(CommandError):
        init_and_launch_command([])


@mock.patch("getpass.getpass")
@mock.patch("django_settings_custom.management.commands.generate_settings.get_input")
@mock.patch(
    "django.conf.settings", FakeSettings(SETTINGS_TEMPLATE_FILE=TEMPLATE_FILE_PATH)
)
def test_error_missing_file_path(input_mock, getpass_mock):
    """Test missing file path."""
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
        SETTINGS_FILE_PATH=CREATED_FILE_PATH,
    ),
)
def test_error_wrong_path(input_mock, getpass_mock):
    """Test not existing file path."""
    input_mock.side_effect = ["y", "user"]
    getpass_mock.return_value = "pass"
    with pytest.raises(CommandError):
        init_and_launch_command([])


@mock.patch("getpass.getpass")
@mock.patch("django_settings_custom.management.commands.generate_settings.get_input")
@mock.patch(
    "django.conf.settings",
    FakeSettings(
        SETTINGS_TEMPLATE_FILE=TEMPLATE_FILE_PATH, SETTINGS_FILE_PATH=CREATED_FILE_PATH
    ),
)
def test_generate_file(input_mock, getpass_mock):
    """Test good parameters generation."""
    input_mock.side_effect = ["y", "user"]
    getpass_mock.return_value = "pass"
    init_and_launch_command([])
    assert os.path.exists(CREATED_FILE_PATH)
    os.remove(CREATED_FILE_PATH)


@mock.patch("getpass.getpass")
@mock.patch("django_settings_custom.management.commands.generate_settings.get_input")
@mock.patch("django_settings_custom.encryption.decrypt")
@mock.patch(
    "django.conf.settings",
    FakeSettings(
        SETTINGS_TEMPLATE_FILE=TEMPLATE_FILE_PATH, SETTINGS_FILE_PATH=CREATED_FILE_PATH
    ),
)
def test_error_generate_file_not_decryptable(decrypt_mock, input_mock, getpass_mock):
    """Test bad encryption during file generation."""
    decrypt_mock.side_effect = ValueError
    input_mock.side_effect = ["y", "user"]
    getpass_mock.return_value = "pass"
    with pytest.raises(CommandError):
        init_and_launch_command([])


@mock.patch("getpass.getpass")
@mock.patch("django_settings_custom.management.commands.generate_settings.get_input")
@mock.patch(
    "django.conf.settings",
    FakeSettings(
        SETTINGS_TEMPLATE_FILE=TEMPLATE_FILE_PATH, SETTINGS_FILE_PATH=CREATED_FILE_PATH
    ),
)
def test_generate_file_override(input_mock, getpass_mock):
    """Test good parameters generation and override existing file."""
    created_file = open(CREATED_FILE_PATH, "w")
    created_file.write("An existing settings file")
    created_file.close()
    input_mock.side_effect = ["y", "y", "user"]
    getpass_mock.return_value = "pass"

    init_and_launch_command([])
    assert os.path.exists(CREATED_FILE_PATH)
    os.remove(CREATED_FILE_PATH)


@mock.patch("django_settings_custom.management.commands.generate_settings.get_input")
@mock.patch(
    "django.conf.settings",
    FakeSettings(
        SETTINGS_TEMPLATE_FILE=TEMPLATE_FILE_PATH, SETTINGS_FILE_PATH=CREATED_FILE_PATH
    ),
)
def test_cancel_generate_file_override(input_mock):
    """Test cancel question."""
    created_file = open(CREATED_FILE_PATH, "w")
    created_file.write("An existing settings file")
    created_file.close()
    input_mock.side_effect = ["n"]

    with pytest.raises(CommandError):
        init_and_launch_command([])
    os.remove(CREATED_FILE_PATH)


@mock.patch("django_settings_custom.management.commands.generate_settings.get_input")
@mock.patch(
    "django.conf.settings",
    FakeSettings(
        SETTINGS_TEMPLATE_FILE=TEMPLATE_FILE_PATH, SETTINGS_FILE_PATH=CREATED_FILE_PATH
    ),
)
def test_error_generate_file_with_secretkey_entered(input_mock):
    """Test empty secret key"""
    input_mock.side_effect = ["n", ""]
    with pytest.raises(CommandError):
        init_and_launch_command([])


@mock.patch("getpass.getpass")
@mock.patch("django_settings_custom.management.commands.generate_settings.get_input")
@mock.patch(
    "django.conf.settings",
    FakeSettings(
        SETTINGS_TEMPLATE_FILE=TEMPLATE_FILE_PATH, SETTINGS_FILE_PATH=CREATED_FILE_PATH
    ),
)
def test_generate_file_with_secretkey_entered(input_mock, getpass_mock):
    """Test with user secret key."""
    input_mock.side_effect = ["n", FakeSettings.SECRET_KEY, "user"]
    getpass_mock.return_value = "pass"
    init_and_launch_command([])
    assert os.path.exists(CREATED_FILE_PATH)

    config = configparser.RawConfigParser()
    config.read(CREATED_FILE_PATH)

    secret_key = config.get("DJANGO", "KEY")
    assert secret_key == FakeSettings.SECRET_KEY
    assert config.get("DATABASE_CREDENTIALS", "USER") == "user"
    assert (
        encryption.decrypt(config.get("DATABASE_CREDENTIALS", "PASSWORD"), secret_key)
        == "pass"
    )

    os.remove(CREATED_FILE_PATH)


@mock.patch("getpass.getpass")
@mock.patch("django_settings_custom.management.commands.generate_settings.get_input")
@mock.patch("django.conf.settings", FakeSettings())
def test_generate_file_command_args(input_mock, getpass_mock):
    """Test force-secretkey option."""
    input_mock.side_effect = ["user"]
    getpass_mock.return_value = "pass"
    init_and_launch_command(
        [TEMPLATE_FILE_PATH, CREATED_FILE_PATH, "--force-secretkey"]
    )
    assert os.path.exists(CREATED_FILE_PATH)
    os.remove(CREATED_FILE_PATH)


@mock.patch("getpass.getpass")
@mock.patch("django_settings_custom.management.commands.generate_settings.get_input")
@mock.patch("django.conf.settings", FakeSettings())
def test_generate_file_with_subclass(input_mock, getpass_mock):
    """Test inheritance."""

    class CustomCommand(generate_settings.Command):
        """Custom test class to specify settings."""

        settings_template_file = TEMPLATE_FILE_PATH
        settings_file_path = CREATED_FILE_PATH
        force_secret_key = True

    input_mock.side_effect = ["user"]
    getpass_mock.return_value = "pass"
    init_and_launch_command([], CustomCommand)
    assert os.path.exists(CREATED_FILE_PATH)
    os.remove(CREATED_FILE_PATH)
