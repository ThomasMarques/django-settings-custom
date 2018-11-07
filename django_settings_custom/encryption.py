# -*- coding: utf-8 -*-
"""
.. module:: encryption
   :synopsis: Module to encrypt / decrypt values.
"""

import base64

from Crypto.Cipher import AES
from Crypto.Hash import SHA256
from Crypto import Random

from django.conf import settings


def _compute_key(secret_key=None):
    """
    Compute a valid key for AES crypto algorithm.

    Args:
        secret_key (str): The key for encryption, or None if you want use the SECRET_KEY.

    Returns:
        byte string: A valid key for AES.

    If the secret_key is not provided, it uses Django settings.SECRET_KEY.
    """
    if secret_key is None:
        secret_key = settings.SECRET_KEY
    return SHA256.new(bytes(secret_key, 'utf-8')).digest()


def encrypt(source, secret_key=None):
    """
    Encrypt the source with the key passed as parameter.

    Args:
        source (str or byte string): A string or a bytes array to encrypt.
        secret_key (str): The key for encryption, or None if you want use the SECRET_KEY.

    Returns:
        str: Encrypted value.

    If the secret_key is not provided, it uses Django settings.SECRET_KEY.
    """
    if isinstance(source, str):
        source = bytes(source, 'utf-8')
    key = _compute_key(secret_key)
    iv = Random.new().read(AES.block_size)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    padding = AES.block_size - len(source) % AES.block_size
    source += bytes([padding]) * padding
    data = iv + cipher.encrypt(source)
    return base64.b64encode(data).decode('latin-1')


def decrypt(source, secret_key=None):
    """
    Decrypt the source with the key passed as parameter.

    Args:
        source (str or byte string): A string or a bytes array to decrypt.
        secret_key (str): The key for encryption, or None if you want use the SECRET_KEY.

    Returns:
        str: Decrypted value.

    If the secret_key is not provided, it uses Django settings.SECRET_KEY.
    """
    key = _compute_key(secret_key)
    source = base64.b64decode(source.encode('latin-1'))
    iv = source[:AES.block_size]
    cipher = AES.new(key, AES.MODE_CBC, iv)
    data = cipher.decrypt(source[AES.block_size:])
    padding = data[-1]
    if data[-padding:] != bytes([padding]) * padding:
        raise ValueError('Error in decryption.')
    return data[:-padding].decode("utf-8")

