# -*- coding: utf-8 -*-
"""Test encryption module."""
import pytest

from django_settings_custom import encryption

SECRET_KEY = "b(l$!na5rzuo+h(psyrlees(p9talk)u!=pjk#6=0v!n*q#y!m"
SOURCE = "A protected sentence !"


def test_string_can_be_decrypt():
    """Basic encryption decryption test."""
    encrypted_source = encryption.encrypt(SOURCE, SECRET_KEY)
    assert SOURCE != encrypted_source

    decrypted_source = encryption.decrypt(encrypted_source, SECRET_KEY)
    assert SOURCE == decrypted_source


def test_bytes_can_be_decrypt():
    """Basic decryption test."""
    encrypted_source = encryption.encrypt(SOURCE.encode(), SECRET_KEY)
    assert SOURCE != encrypted_source

    decrypted_source = encryption.decrypt(encrypted_source, SECRET_KEY)
    assert SOURCE == decrypted_source


def test_decryption_error():
    """Basic decryption error."""
    with pytest.raises(ValueError):
        encryption.decrypt("Bad value", SECRET_KEY)
