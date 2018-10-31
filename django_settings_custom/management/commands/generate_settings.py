# -*- coding: utf-8 -*-
import configparser
import os
import re

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.core.management.utils import get_random_secret_key

from django_settings_custom import encryption


class Command(BaseCommand):
    """
    A Django interactive command for configuration file generation.
    """
    settings_template_file = settings.SETTINGS_TEMPLATE_FILE
    settings_file_path = settings.SETTINGS_FILE_PATH

    @staticmethod
    def get_value(section, key, value_type, secret_key):
        """
        Get a value for the [section] key passed as parameter.
        :param section: Section in the configuration file.
        :param key: Key in the configuration file.
        :param value_type: Value type read in template.
        :param secret_key: Django secret key
        :return: Value for the [section] key
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
        assert self.settings_template_file and os.path.exists(self.settings_template_file)
        assert self.settings_file_path

        self.stdout.write('** Configuration file generation: **')
        if os.path.exists(self.settings_file_path):
            override = input('A configuration file already exists at %s. Would you override it ? (y/N) : ' %
                             self.settings_file_path)
            if override.upper() != 'Y':
                raise CommandError('Generation cancelled.')

        config = configparser.ConfigParser()
        config.optionxform = str
        config.read(self.settings_template_file)

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
        self.stdout.write('\nWriting file at %s:' % self.settings_file_path)
        os.makedirs(os.path.dirname(self.settings_file_path), exist_ok=True)
        with open(self.settings_file_path, 'w') as config_file:
            config.write(config_file)
        self.stdout.write(self.style.SUCCESS('Configuration file successfully generated !'))
