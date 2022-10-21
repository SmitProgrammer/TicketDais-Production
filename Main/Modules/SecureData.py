import base64

from cryptography.fernet import Fernet


class SecureData():
    def __init__(self, user, key):
        self.user = user.encode('utf-8')
        # self.key = user['localId']
        self.key = (base64.urlsafe_b64encode(key.encode('utf-8')))[:32]
        self.secure = Fernet(self.key)

    def get_key(self):
        pass

    def encrypt(self, text):
        return self.secure.encrypt(text.encode('utf-8'))

    def decrypt(self, token):
        return self.secure.decrypt(token.decode('utf-8'))
