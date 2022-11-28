import os.path

from cryptography.fernet import Fernet


class SecureData():
    def __init__(self, key):
        # self.key = key
        self.key = key  # (base64.urlsafe_b64encode(key.encode('utf-8')))
        self.secure = Fernet(self.key)

    def GenerateKey(self):
        return Fernet.generate_key().decode('utf-8')

    def encrypt(self, text):
        return self.secure.encrypt(str(text).encode('utf-8')).decode('utf-8')

    def decrypt(self, token):
        return self.secure.decrypt(token).decode('utf-8')


class Vault():
    def __init__(self):
        if os.path.exists("key"):
            key = open("key", "r")
            self.key = key.read()
        else:
            self.GenerateKey()

    def GenerateKey(self):
        self.key = Fernet.generate_key().decode("utf-8")
        with open("key", "w") as key_file:
            key_file.write(self.key)
        key_file.close()
