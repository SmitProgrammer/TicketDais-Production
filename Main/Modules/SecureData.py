import os.path

from cryptography.fernet import Fernet


class SecureData():
    """SecureData class for encrypting and decrypting data
    :param key: The key used to encrypt and decrypt data"""
    def __init__(self, key):
        """Initialize the SecureData class
        and set the key to encrypt and decrypt data"""
        # self.key = key
        self.key = key  # (base64.urlsafe_b64encode(key.encode('utf-8')))
        self.secure = Fernet(self.key)

    def GenerateKey(self):
        """Generate a key for encrypting and decrypting data and return the key"""
        return Fernet.generate_key().decode('utf-8')

    def encrypt(self, text):
        """Encrypt the text using the key and return the encrypted"""
        return self.secure.encrypt(str(text).encode('utf-8')).decode('utf-8')

    def decrypt(self, token):
        """Decrypt the token using the key and return the decrypted text"""
        return self.secure.decrypt(token).decode('utf-8')


class Vault():
    """Vault class used to check if master key exists and generate one if it doesn't exist and save it to a key file"""

    def __init__(self):
        """Initialize the Vault class and check if the key file exists and generate one if it doesn't exist"""
        if os.path.exists("key"):
            key = open("key", "r")
            self.key = key.read()
        else:
            self.GenerateKey()

    def GenerateKey(self):
        """Generate a key for encrypting and decrypting data and save it to a key file"""
        self.key = Fernet.generate_key().decode("utf-8")
        with open("key", "w") as key_file:
            key_file.write(self.key)
        key_file.close()
