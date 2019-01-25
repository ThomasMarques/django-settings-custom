# -*- coding: utf-8 -*-
import pytest

from django_settings_custom import encryption


secret_key = "b(l$!na5rzuo+h(psyrlees(p9talk)u!=pjk#6=0v!n*q#y!m"
source = "A protected sentence !"


def test_string_can_be_decrypt():
    encrypted_source = encryption.encrypt(source, secret_key)
    assert source != encrypted_source

    decrypted_source = encryption.decrypt(encrypted_source, secret_key)
    assert source == decrypted_source


def test_bytes_can_be_decrypt():
    encrypted_source = encryption.encrypt(source.encode(), secret_key)
    assert source != encrypted_source

    decrypted_source = encryption.decrypt(encrypted_source, secret_key)
    assert source == decrypted_source


def test_decryption_error():
    with pytest.raises(ValueError):
        encryption.decrypt("Bad value", secret_key)
