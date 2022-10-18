from cryptography.fernet import Fernet

class SecureData():
    def __init__(self, user):
        self.user = user
        self.key = user['localId']
        self.secure = Fernet(self.key)

    def encrypt(self, text):
        return self.secure.encrypt(text.encode('utf-8'))

    def decrypt(self, token):
        return self.secure.decrypt(token.decode('utf-8'))