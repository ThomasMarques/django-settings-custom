# -*- coding: utf-8 -*-
from unittest import TestCase

from django_settings_custom import encryption


class TestEncryption(TestCase):
    def test_encryption_can_be_decrypt(self):
        secret_key = "b(l$!na5rzuo+h(psyrlees(p9talk)u!=pjk#6=0v!n*q#y!m"
        source = "A protected sentence !"

        encrypted_source = encryption.encrypt(source, secret_key)
        self.assertNotEqual(source, encrypted_source)

        decrypted_source = encryption.decrypt(encrypted_source, secret_key)
        self.assertEqual(source, decrypted_source)
