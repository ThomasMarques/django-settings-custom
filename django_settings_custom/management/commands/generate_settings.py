# -*- coding: utf-8 -*-
try:
    from configparser import ConfigParser
except ImportError:  # Python 2 compatibility
    from ConfigParser import ConfigParser
import os
import re

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.core.management.utils import get_random_secret_key

from django_settings_custom import encryption


class Command(BaseCommand):
    """
    A Django interactive command for configuration file generation.

    Example:
        python manage.py generate_settings path/to/template/settings.ini target/path/of/settings.ini'

    Attributes:
        settings_template_file (str): Path to the settings template file.
        settings_file_path (str): Target path for the created settings file.
    """
    help = 'A Django interactive command for configuration file generation.'
    usage = 'python manage.py generate_settings path/to/template/settings.ini target/path/of/settings.ini'

    settings_template_file = settings.SETTINGS_TEMPLATE_FILE if hasattr(settings, 'SETTINGS_TEMPLATE_FILE') else None
    settings_file_path = settings.SETTINGS_FILE_PATH if hasattr(settings, 'SETTINGS_FILE_PATH') else None

    def add_arguments(self, parser):
        """
        Add custom arguments to the command.
        See python manage.py generate_settings --help.
        """
        parser.usage = self.usage
        parser.add_argument(
            'settings_template_file',
            nargs='?',
            type=str,
            default=None,
            help="Path to the settings template file.")
        parser.add_argument(
            'settings_file_path',
            nargs='?',
            type=str,
            default=None,
            help="Target path for the settings file.")

    @staticmethod
    def get_value(section, key, value_type, secret_key):
        """
        Get a value for the [section] key passed as parameter.

        Args:
            section (str): Section in the configuration file.
            key (str): Key in the configuration file.
            value_type (str): Value type read in template, must be "DJANGO_SECRET_KEY", "USER_VALUE" or "ENCRYPTED_USER_VALUE".
            secret_key: Django secret key

        Returns:
            int or str: Value for the [section] key
        """
        value = None
        if value_type == 'DJANGO_SECRET_KEY':
            value = secret_key
        elif 'USER_VALUE' in value_type:
            encrypt = value_type == 'ENCRYPTED_USER_VALUE'
            encrypt_message = ''
            if encrypt:
                encrypt_message = '(will be encrypted) '
            value = input('Value for [%s] %s %s: ' % (section, key, encrypt_message))
            if encrypt:
                value = encryption.encrypt(value, secret_key)
        return value

    def handle(self, *args, **options):
        """
        Command core.
        """
        settings_template_file = options['settings_template_file']
        settings_file_path = options['settings_file_path']
        if not settings_template_file and not settings_file_path:
            settings_template_file = self.settings_template_file
            settings_file_path = self.settings_file_path
        if not settings_template_file:
            raise CommandError('Parameter settings_template_file undefined.\nUsage: %s' % self.usage)
        if not settings_file_path:
            raise CommandError('Parameter settings_file_path undefined.\nUsage: %s' % self.usage)
        if not os.path.exists(settings_template_file):
            raise CommandError('The settings template file doesn\'t exists.')

        self.stdout.write('** Configuration file generation: **')
        if os.path.exists(settings_file_path):
            override = input('A configuration file already exists at %s. Would you override it ? (y/N) : ' %
                             settings_file_path)
            if override.upper() != 'Y':
                raise CommandError('Generation cancelled.')

        config = ConfigParser()
        config.optionxform = str
        config.read(settings_template_file)

        generate_secret_key = input('Do you want to generate the secret key for Django ? (Y/n) : ')
        if generate_secret_key.upper() == 'N':
            secret_key = input('Enter your secret key : ')
            if not secret_key:
                raise CommandError('Django secret key is needed for encryption. Generation cancelled.')
        else:
            secret_key = get_random_secret_key()
            self.stdout.write('Django secret key generated !')
        secret_key = secret_key.replace('%', '%%')

        self.stdout.write('\n** Enter values for configuration file content **')
        variable_regex = re.compile(r' *{(.+)} *')
        for section, values in config.items():
            for key, value in values.items():
                match_groups = variable_regex.match(value)
                if match_groups:
                    value_type = match_groups.group(1).strip().upper()
                    config.set(section, key, self.get_value(section, key, value_type, secret_key))
        self.stdout.write('\nWriting file at %s:' % settings_file_path)
        os.makedirs(os.path.dirname(settings_file_path), exist_ok=True)
        with open(settings_file_path, 'w') as config_file:
            config.write(config_file)
        self.stdout.write(self.style.SUCCESS('Configuration file successfully generated !'))
