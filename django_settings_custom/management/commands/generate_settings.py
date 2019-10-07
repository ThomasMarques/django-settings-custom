# -*- coding: utf-8 -*-
"""Generate settings command."""
import getpass
import os
import re

from six.moves.configparser import RawConfigParser

from django.core.management.base import BaseCommand, CommandError
from django.core.management.utils import get_random_secret_key

from django_settings_custom import encryption


def get_input(text):
    """Prompt text and return text write by the user."""
    return input(text)


class Command(BaseCommand):
    """
    A Django interactive command for configuration file generation.

    Example:
        python manage.py generate_settings
        path/to/template/settings.ini target/path/of/settings.ini'

    Attributes:
        settings_template_file (str): Path to the settings template file.
        settings_file_path (str): Target path for the created settings file.
        force_secret_key (bool): Generate SECRET_KEY without asking ?
    """

    help = "A Django interactive command for configuration file generation."
    usage = (
        "python manage.py generate_settings"
        "path/to/template/settings.ini target/path/of/settings.ini"
    )

    settings_template_file = None
    settings_file_path = None
    force_secret_key = None

    def __init__(self, *argc, **kwargs):
        super(Command, self).__init__(*argc, **kwargs)

        from django.conf import settings

        self.django_keys = []
        self.encrypted_field = []
        if self.settings_template_file is None:
            self.default_settings_template_file = (
                settings.SETTINGS_TEMPLATE_FILE
                if hasattr(settings, "SETTINGS_TEMPLATE_FILE")
                else None
            )
        else:
            self.default_settings_template_file = self.settings_template_file

        if self.settings_file_path is None:
            self.default_settings_file_path = (
                settings.SETTINGS_FILE_PATH
                if hasattr(settings, "SETTINGS_FILE_PATH")
                else None
            )
        else:
            self.default_settings_file_path = self.settings_file_path

        if self.force_secret_key is None:
            self.default_force_secret_key = (
                settings.SETTINGS_FORCE_SECRET_KEY
                if hasattr(settings, "SETTINGS_FORCE_SECRET_KEY")
                else False
            )
        else:
            self.default_force_secret_key = self.force_secret_key

    def add_arguments(self, parser):
        """
        Add custom arguments to the command.
        See python manage.py generate_settings --help.
        """
        parser.usage = self.usage
        parser.add_argument(
            "settings_template_file",
            nargs="?",
            type=str,
            default=self.default_settings_template_file,
            help="Path to the settings template file.",
        )
        parser.add_argument(
            "settings_file_path",
            nargs="?",
            type=str,
            default=self.default_settings_file_path,
            help="Target path for the settings file.",
        )
        parser.add_argument(
            "--force-secretkey",
            action="store_true",
            dest="force_secretkey",
            help="Generate SECRET_KEY without asking.",
        )

    def get_value(self, section, key, value_type):
        """
        Get a value for the [section] key passed as parameter.

        Args:
            section (str): Section in the configuration file.
            key (str): Key in the configuration file.
            value_type (str): Value type read in template,
                must be "DJANGO_SECRET_KEY", "USER_VALUE" or "ENCRYPTED_USER_VALUE".

        Returns:
            int or str: Value for the [section] key
        """
        value = None
        if value_type == "DJANGO_SECRET_KEY":
            self.django_keys.append((section, key))
        elif "USER_VALUE" in value_type:
            to_encrypt = value_type == "ENCRYPTED_USER_VALUE"
            if to_encrypt:
                value = getpass.getpass(
                    "Value for [%s] %s (will be encrypted) : " % (section, key)
                )
                self.encrypted_field.append((section, key))
            else:
                value = get_input("Value for [%s] %s : " % (section, key))
        return value

    def handle(self, *args, **options):
        """
        Command core.
        """
        settings_template_file = options["settings_template_file"]
        settings_file_path = options["settings_file_path"]
        force_secret_key = options["force_secretkey"]
        if not force_secret_key:
            force_secret_key = self.default_force_secret_key
        if not settings_template_file:
            raise CommandError(
                "Parameter settings_template_file undefined.\nUsage: %s" % self.usage
            )
        if not settings_file_path:
            raise CommandError(
                "Parameter settings_file_path undefined.\nUsage: %s" % self.usage
            )
        if not os.path.exists(settings_template_file):
            raise CommandError("The settings template file doesn't exists.")

        self.stdout.write("** Configuration file generation: **")
        if os.path.exists(settings_file_path):
            override = get_input(
                "A configuration file already exists at %s. "
                "Would you override it ? (y/N) : " % settings_file_path
            )
            if override.upper() != "Y":
                raise CommandError("Generation cancelled.")

        config = RawConfigParser()
        config.read(settings_template_file)

        input_secret_key = False
        secret_key = None
        if not force_secret_key:
            generate_secret_key = get_input(
                "Do you want to generate the secret key for Django ? (Y/n) : "
            )
            input_secret_key = generate_secret_key.upper() == "N"
        if input_secret_key:
            secret_key = get_input("Enter your secret key : ")
            if not secret_key:
                raise CommandError(
                    "Django secret key is needed for encryption. Generation cancelled."
                )
        else:
            self.stdout.write("Django secret key generation !")

        self.stdout.write("\n** Filling values for configuration file content **")
        variable_regex = re.compile(r" *{(.+)} *")
        properties = {}
        for section in config.sections():
            properties[section] = {}
            for key, value in config.items(section):
                match_groups = variable_regex.match(value)
                if match_groups:
                    value_type = match_groups.group(1).strip().upper()
                    value = self.get_value(section, key, value_type)
                    properties[section][key] = value
        max_retry = 0 if input_secret_key else 3
        retry = 0
        encrypted_properties = properties.copy()
        while retry <= max_retry and self.encrypted_field:
            if secret_key is None:
                secret_key = get_random_secret_key().replace("%", "0")
            try:
                for section, key in self.encrypted_field:
                    value = encryption.encrypt(properties[section][key], secret_key)
                    encryption.decrypt(value, secret_key)
                    encrypted_properties[section][key] = value
                retry = max_retry
            except ValueError:
                secret_key = None
            retry += 1

        if secret_key is None:
            raise CommandError(
                "Error while encoding / decoding passwords with the secret key."
                "Retried %s. Generation cancelled." % max_retry
            )

        for section, key in self.django_keys:
            encrypted_properties[section][key] = secret_key

        # Fill config file
        for section, values in encrypted_properties.items():
            for key, value in values.items():
                config.set(section, key, value)
        self.stdout.write("\nWriting file at %s:" % settings_file_path)
        settings_directory = os.path.dirname(settings_file_path)
        if not os.path.exists(settings_directory):
            os.makedirs(settings_directory)
        with open(settings_file_path, "w") as config_file:
            config.write(config_file)
        self.stdout.write(
            self.style.SUCCESS("Configuration file successfully generated !")
        )
