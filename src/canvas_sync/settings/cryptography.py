"""
Canvas-Sync by Sang-Buster
February 2017

--------------------------------------------

cryptography.py, module

Functions used to encrypt and decrypt the settings stored in the .Canvas-Sync.settings file. When the user has specified
settings the string of information is encrypted using the AES 256 module of the PyCrypto library. A password is
specified by the user upon creation of the settings file. A hashed (thus unreadable) version of the password is stored
locally in the .ps.sync file in the home folder of the user. Upon launch of Canvas-Sync, the user must specify
a password that matches the one stored in the hashed version. If the password is correct the the settings file is
decrypted and parsed for settings.
"""

# Future imports

# Inbuilt modules
import getpass
import os.path
import sys

# Third party modules
import bcrypt
from Crypto.Cipher import AES
from Crypto.Hash import SHA256


def get_key_hash(password):
    """Get a 256 byte SHA hash from any length password"""
    # Accept either str or bytes
    if isinstance(password, str):
        password_bytes = password.encode("utf-8")
    else:
        password_bytes = password
    hasher = SHA256.new()
    hasher.update(password_bytes)
    return hasher.digest()


def encrypt(message):
    """
    Encrypts a string using AES-256 (CBC) encryption
    A random initialization vector (IV) is padded as the initial 16 bytes of the string
    The encrypted message will be padded to length%16 = 0 bytes (AES needs 16 bytes block sizes)
    """

    print("\nPlease enter a password to encrypt the settings file:")
    password = getpass.getpass()
    password_bytes = password.encode("utf-8")
    hashed_password = bcrypt.hashpw(password_bytes, bcrypt.gensalt())
    with open(
        os.path.join(os.path.expanduser("~"), ".Canvas-Sync.pw"), "wb"
    ) as pass_file:
        pass_file.write(hashed_password)

    # Generate random 16 bytes IV
    IV = os.urandom(16)

    # AES object
    encrypter = AES.new(get_key_hash(hashed_password), AES.MODE_CBC, IV)

    # Padding to 16 bytes
    if len(message.encode("utf-8")) % 16 != 0:
        pad_len = 16 - (len(message.encode("utf-8")) % 16)
        message = message + (" " * pad_len)

    # Add the unencrypted IV to the beginning of the encrypted_message
    encrypted_message = IV + encrypter.encrypt(message.encode("utf-8"))

    return encrypted_message


def decrypt(message, password):
    """
    Decrypts an AES encrypted string
    """

    # Load the locally stored bcrypt hashed password (answer)
    path = os.path.join(os.path.expanduser("~"), ".Canvas-Sync.pw")
    if not os.path.exists(path):
        return False

    with open(path, "rb") as pw_file:
        hashed_password = pw_file.read()

    # If the password isn't null then it was specified as a command-line argument
    if password:
        password_bytes = (
            password.encode("utf-8") if isinstance(password, str) else password
        )
        if not bcrypt.checkpw(password_bytes, hashed_password):
            print(
                "\n[ERROR] Invalid password. Please try again or invoke Canvas-Sync with the -s flag to reset settings."
            )
            sys.exit()
    else:
        # Otherwise, get the password from the user
        valid_password = False
        while not valid_password:
            print("\nPlease enter password to decrypt the settings file:")
            password = getpass.getpass()
            password_bytes = password.encode("utf-8")
            if bcrypt.checkpw(password_bytes, hashed_password):
                valid_password = True
            else:
                print(
                    "\n[ERROR] Invalid password. Please try again or invoke Canvas-Sync with the -s flag to reset settings."
                )

    # Read the remote IV
    remoteIV = message[:16]

    # Decrypt message using the correct password-derived key
    decrypter = AES.new(get_key_hash(hashed_password), AES.MODE_CBC, remoteIV)
    decrypted_message = decrypter.decrypt(message[16:])

    return decrypted_message.rstrip()
