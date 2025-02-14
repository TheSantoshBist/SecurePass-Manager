import json
from cryptography.fernet import Fernet
import base64
import os
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import secrets

class ImportExportManager:
    def __init__(self, master_key: str):
        self.master_key = master_key
        self.salt = b'exportsecuresalt'  # Different salt for export
        self.key = self._generate_key(master_key)
        self.fernet = Fernet(self.key)

    def _generate_key(self, master_key: str) -> bytes:
        # Use PBKDF2HMAC for key derivation
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=self.salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(master_key.encode()))
        return key

    def export_passwords(self, passwords: list, filename: str) -> bool:
        try:
            # Convert bytes to strings before encryption
            serializable_passwords = []
            for password in passwords:
                serializable_password = password.copy()
                for key, value in serializable_password.items():
                    if isinstance(value, bytes):
                        serializable_password[key] = value.decode('utf-8')
                serializable_passwords.append(serializable_password)

            # Encrypt the passwords
            encrypted_data = self.fernet.encrypt(json.dumps(serializable_passwords).encode())

            # Write the encrypted data to the file
            with open(filename, 'wb') as f:
                f.write(encrypted_data)
            return True
        except Exception as e:
            print(f"Error exporting passwords: {e}")
            return False

    def import_passwords(self, filename: str) -> list:
        try:
            # Read the encrypted data from the file
            with open(filename, 'rb') as f:
                encrypted_data = f.read()

            # Decrypt the data
            decrypted_data = self.fernet.decrypt(encrypted_data).decode()

            # Load the passwords from the decrypted data
            passwords = json.loads(decrypted_data)

            return passwords
        except Exception as e:
            print(f"Error importing passwords: {e}")
            return []