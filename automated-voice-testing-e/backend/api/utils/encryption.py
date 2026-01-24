"""
Encryption utilities for secure data storage

This module provides encryption and decryption functions using Fernet
symmetric encryption from the cryptography library.

The module includes:
    - encrypt(): Encrypts a value using Fernet symmetric encryption
    - decrypt(): Decrypts an encrypted value
    - Key management: Generates or loads encryption key from environment

Example:
    >>> from api.utils.encryption import encrypt, decrypt
    >>>
    >>> # Encrypt a value
    >>> encrypted = encrypt("my_secret_value")
    >>> print(encrypted)  # Returns encrypted bytes
    >>>
    >>> # Decrypt the value
    >>> decrypted = decrypt(encrypted)
    >>> print(decrypted)
    'my_secret_value'

Note:
    - Fernet uses symmetric encryption (same key for encrypt/decrypt)
    - Encrypted values are returned as strings (base64 encoded)
    - The encryption key should be stored securely (environment variable)
    - Each encryption generates a unique ciphertext (due to random IV)
"""

import os
import base64
from typing import Optional, Union
from cryptography.fernet import Fernet, InvalidToken


# Global Fernet instance (initialized once)
_fernet_instance: Optional[Fernet] = None


def _get_encryption_key() -> bytes:
    """
    Get or generate the encryption key.

    Returns the encryption key from the ENCRYPTION_KEY environment variable.
    If not set, generates a new key (WARNING: this should only be used for
    development/testing, as the key won't persist across restarts).

    Returns:
        bytes: Fernet encryption key

    Example:
        >>> key = _get_encryption_key()
        >>> isinstance(key, bytes)
        True
    """
    # Try to get key from environment
    env_key = os.environ.get('ENCRYPTION_KEY')

    if env_key:
        # Decode the base64-encoded key from environment
        try:
            return base64.urlsafe_b64decode(env_key)
        except Exception:
            # If decoding fails, treat it as the raw key
            return env_key.encode() if isinstance(env_key, str) else env_key

    # Generate a new key if not in environment (for development only)
    # WARNING: This key won't persist across restarts
    return Fernet.generate_key()


def _get_fernet() -> Fernet:
    """
    Get or create the Fernet instance.

    Returns a singleton Fernet instance using the encryption key.

    Returns:
        Fernet: Fernet encryption instance

    Example:
        >>> f = _get_fernet()
        >>> isinstance(f, Fernet)
        True
    """
    global _fernet_instance

    if _fernet_instance is None:
        key = _get_encryption_key()
        _fernet_instance = Fernet(key)

    return _fernet_instance


def encrypt(value: Union[str, bytes]) -> str:
    """
    Encrypt a value using Fernet symmetric encryption.

    Args:
        value: The value to encrypt (string or bytes)

    Returns:
        str: Base64-encoded encrypted value

    Raises:
        TypeError: If value is not string or bytes
        Exception: If encryption fails

    Example:
        >>> encrypted = encrypt("my_secret")
        >>> isinstance(encrypted, str)
        True
        >>> len(encrypted) > 0
        True

    Note:
        - Input strings are encoded to UTF-8 before encryption
        - Output is base64-encoded string for easy storage
        - Each call generates unique ciphertext (Fernet uses random IV)
    """
    try:
        # Convert string to bytes if needed
        if isinstance(value, str):
            value_bytes = value.encode('utf-8')
        elif isinstance(value, bytes):
            value_bytes = value
        else:
            raise TypeError(f"Value must be string or bytes, got {type(value)}")

        # Encrypt using Fernet
        fernet = _get_fernet()
        encrypted_bytes = fernet.encrypt(value_bytes)

        # Return as string (already base64-encoded by Fernet)
        return encrypted_bytes.decode('utf-8')

    except Exception as e:
        raise Exception(f"Encryption failed: {str(e)}")


def decrypt(encrypted_value: Union[str, bytes]) -> str:
    """
    Decrypt an encrypted value using Fernet symmetric encryption.

    Args:
        encrypted_value: The encrypted value to decrypt (string or bytes)

    Returns:
        str: Decrypted value as string

    Raises:
        TypeError: If encrypted_value is not string or bytes
        InvalidToken: If encrypted_value is invalid or corrupted
        Exception: If decryption fails

    Example:
        >>> encrypted = encrypt("my_secret")
        >>> decrypted = decrypt(encrypted)
        >>> decrypted
        'my_secret'

    Note:
        - Input can be base64-encoded string or bytes
        - Output is always decoded to UTF-8 string
        - Raises InvalidToken if data is corrupted or wrong key used
    """
    try:
        # Convert string to bytes if needed
        if isinstance(encrypted_value, str):
            encrypted_bytes = encrypted_value.encode('utf-8')
        elif isinstance(encrypted_value, bytes):
            encrypted_bytes = encrypted_value
        else:
            raise TypeError(f"Encrypted value must be string or bytes, got {type(encrypted_value)}")

        # Decrypt using Fernet
        fernet = _get_fernet()
        decrypted_bytes = fernet.decrypt(encrypted_bytes)

        # Return as string
        return decrypted_bytes.decode('utf-8')

    except InvalidToken:
        raise InvalidToken("Decryption failed: Invalid token or corrupted data")
    except Exception as e:
        raise Exception(f"Decryption failed: {str(e)}")
