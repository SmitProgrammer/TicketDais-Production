import base64
import os

import pyotp
import qrcode

from Main.Modules import SecureData, EmailServices
from TicketDais.settings import EMAIL_HOST, EMAIL_HOST_PASSWORD

vault = SecureData.Vault()
vault_key = SecureData.SecureData(vault.key)
print("Helper " + vault.key)


def __init__():
    user = None


def get_user_info(user, db):
    try:
        udata = db.child("/users/" + user['localId']).get(user['idToken'])
        ukey = db.child("/vault/" + user['localId']).get(user['idToken'])
        user_vault = SecureData.SecureData(vault.key)
        for key in ukey.each():
            if key.key() == "ENC_KEY":
                print("Encrypt", user_vault.decrypt(key.val()))
                enc_key = user_vault.decrypt(key.val())
            elif key.key() == "2FA_KEY":
                print("2FA", user_vault.decrypt(key.val()))
                info = [key.key(), user_vault.decrypt(key.val())]
                data = [info]
            print("get_user_info ", key.key(), user_vault.decrypt(key.val().encode('utf-8')))
        user_enc = SecureData.SecureData(enc_key.encode())
        print(user_enc.key)
        for user_data in udata.each():
            info = [user_data.key(), user_enc.decrypt(user_data.val())]
            data.append(info)
        data = dict(data)
        return data
    except Exception as e:
        print(e)
        return False


def create_user(user, db, MFA):
    key = create_user_vault(user, db, MFA)
    securedata = SecureData.SecureData(key)
    print(key)
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


def delete_user(user, db, auth):
    db.child("users").child(user['localId']).remove()
    db.child("vault").child(user['localId']).remove()
    auth.delete_user_account(user['idToken'])


def create_user_vault(user, db, MFA):
    key = SecureData.SecureData.GenerateKey(SecureData)
    print("generated key: " + key)
    data = {"vault/" + user["localId"]:
        {
            "ENC_KEY": vault_key.encrypt(key),
            "2FA_KEY": vault_key.encrypt(MFA)
        }
    }
    db.update(data, user['idToken'])
    return key


def get_2fa(user):
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


email_verification = EmailServices.EmailVerification(EMAIL_HOST, EMAIL_HOST_PASSWORD, length=6)


def send_email_verification(email):
    msg = open("./Main/Modules/EmailTemplate/verify_email.html").read()
    email_verification.send_otp(email, "TicketDais - Verification", "TicketDais - Verification", "OTP For TicketDais",
                                msg)


def verify_email(otp):
    return email_verification.verify_otp(otp)


def get_2fa_otp(request, db):
    try:
        key = db.child("/vault/" + request.session.get('userId')).get(request.session.get('id'))
        for key in key.each():
            if key.key() == "2FA_KEY":
                key = vault_key.decrypt(key.val())
                return pyotp.TOTP(key).now()
    except Exception as e:
        print(e)
        return str(e)
