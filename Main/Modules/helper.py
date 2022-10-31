import base64
import os

import pyotp
import qrcode

from Main.Modules import SecureData

vault = SecureData.Vault()
vault_key = SecureData.SecureData(vault.key)
print("Helper " + vault.key)


def GetUserInfo(user, db):
    try:
        udata = db.child("/users/" + user['localId']).get(user['idToken'])
        ukey = db.child("/vault/" + user['localId'] + "/ENC_KEY").get(user['idToken'])
        data = []
        for user_data in udata.each():
            info = [user_data.key(), user_data.val()]
            data.append(info)
        data = dict(data)
        return data
    except:
        return False

def CreateUser(user, db, MFA):
    key = CreateUserVault(user, db, MFA)
    securedata = SecureData.SecureData(key)
    data = {"users/" + user['localId'].strip(): {
        "email_id": securedata.encrypt(user['email']),
        "email_verified": securedata.encrypt(False),
        "name": securedata.encrypt(user["displayName"]),
        "balance": securedata.encrypt(0),
        "banned": securedata.encrypt(False),
        "phone_no": securedata.encrypt(user["phoneNum"]),
        "profile": securedata.encrypt(""),
    }}
    db.update(data, user['idToken'])


def DeleteUser(user, db, auth):
    auth.delete_user_account(user['idToken'])
    db.child("users").child(user['localId']).remove()
    db.child("vault").child(user['localId']).remove()


def CreateUserVault(user, db, MFA):
    key = SecureData.SecureData.GenerateKey(SecureData)
    data = {"vault/" + user["localId"]:
        {
            "ENC_KEY": vault_key.encrypt(key),
            "2FA_KEY": vault_key.encrypt(MFA)
        }
    }
    db.update(data, user['idToken'])
    return key


def Get2FA(user, db):
    email = user["email"]
    if not os.path.exists("tmp"):
        os.makedirs("tmp")
    code = pyotp.random_base32()
    qr = qrcode.make(
        pyotp.totp.TOTP(code).provisioning_uri(name=email, issuer_name="Ticket Dais"))
    qr_name = "tmp/" + email
    qr.save(qr_name, "PNG")
    with open(qr_name, "rb") as img:
        img = base64.b64encode(img.read()).decode("utf-8")
    os.remove(qr_name)
    img = "data:image/png;base64," + img
    # db.update(data, user['idToken'])
    return [code, img]
