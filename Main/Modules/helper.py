import base64
import os

import pyotp
import qrcode


import platform
import psutil

import socket

import pyautogui
from Main.Modules import SecureData, EmailServices
from TicketDais.settings import EMAIL_HOST, EMAIL_HOST_PASSWORD

vault = SecureData.Vault()
vault_key = SecureData.SecureData(vault.key)
print("Helper " + vault.key)


def __init__():
    user = None


def get_user_info(user, db):
    """Get user info from the database and decrypt it using the vault key and the user's encryption key and return it as a dictionary"""
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
    """Create a user in the database and encrypt the data using the vault key and the user's encryption key"""
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


def verify_user(user, db):
    """Verify the user's email and update the database"""
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
        data = []
        for user_data in udata.each():
            info = []
            if user_data.key() == "email_verified":
                info.append(user_data.key())
                info.append(user_enc.encrypt(True))
            else:
                info.append(user_data.key())
                info.append(user_data.val())
            data.append(info)
        print(data)
        db.child("/users/" + user['localId']).update(user['idToken'])
    except Exception as e:
        print(e)
        return False


def delete_user(user, db, auth):
    """Delete the user from the database and the authentication"""
    db.child("users").child(user['localId']).remove()
    db.child("vault").child(user['localId']).remove()
    auth.delete_user_account(user['idToken'])


def create_user_vault(user, db, MFA):
    """Create a vault for the user and return the encryption key"""
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
    """Generate a QR code for the user's 2FA and return the code and the image"""
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
    """Send an email verification to the user's email address using the email template and email_verification module"""
    msg = open("./Main/Modules/EmailTemplate/verify_email.html").read()
    email_verification.send_otp(email, "TicketDais - Verification", "TicketDais - Verification", "OTP For TicketDais", msg)


def verify_email(otp):
    """Verify the user's email using the email_verification module"""
    return email_verification.verify_otp(otp)


def get_2fa_otp(request, db):
    """Get the user's 2FA key from the database and return the current OTP"""
    try:
        key = db.child("/vault/" + request.session.get('userId')).get(request.session.get('id'))
        for key in key.each():
            if key.key() == "2FA_KEY":
                key = vault_key.decrypt(key.val())
                return pyotp.TOTP(key).now()
    except Exception as e:
        print(e)
        return str(e)



def get_device_info():
    """Get the device information"""
    device_info = {}

    # Get operating system name
    device_info['os_name'] = platform.system()

    # Get RAM
    # device_info['ram'] = round(psutil.virtual_memory().total / (1024.0 ** 3)) # Not accurate
    device_info['ram'] = str(round(psutil.virtual_memory().total / (1024.0 ** 3), 2)) + " GB"
    # device_info['ram'] = str(round(psutil.virtual_memory().total)) + " GB"

    # Get processor name
    device_info['processor'] = platform.processor()

    # Get IP address
    device_info['ip_address'] = socket.gethostbyname(socket.gethostname())

    # Get device type (e.g. desktop, laptop, server, etc.)
    device_info['device_type'] = platform.machine()
    device_info['device_type'] = device_info['device_type'].replace("x86_64", "Desktop")
    device_info['device_type'] = device_info['device_type'].replace("AMD64", "Desktop")
    device_info['device_type'] = device_info['device_type'].replace("i386", "Desktop")
    device_info['device_type'] = device_info['device_type'].replace("i686", "Desktop")
    device_info['device_type'] = device_info['device_type'].replace("i586", "Desktop")
    device_info['device_type'] = device_info['device_type'].replace("i486", "Desktop")
    device_info['device_type'] = device_info['device_type'].replace("i386", "Desktop")
    device_info['device_type'] = device_info['device_type'].replace("i286", "Desktop")
    device_info['device_type'] = device_info['device_type'].replace("i186", "Desktop")
    device_info['device_type'] = device_info['device_type'].replace("i86", "Desktop")

    device_info['device_type'] = device_info['device_type'].replace("x86", "Desktop")
    device_info['device_type'] = device_info['device_type'].replace("AMD", "Desktop")
    device_info['device_type'] = device_info['device_type'].replace("Intel", "Desktop")
    
    device_info['device_type'] = device_info['device_type'].replace("ARM", "Mobile")
    device_info['device_type'] = device_info['device_type'].replace("arm", "Mobile")
    device_info['device_type'] = device_info['device_type'].replace("aarch64", "Mobile")
    device_info['device_type'] = device_info['device_type'].replace("AARCH64", "Mobile")

    device_info['device_type'] = device_info['device_type'].replace("Raspberry", "Raspberry Pi")

    # Get company (e.g. Dell, HP, Lenovo, etc.)
    # device_info['company'] = platform.uname().system # Not Working
    device_info['company'] = platform.uname().node

    device_info['device_resolution'] = [str(x) for x in pyautogui.size()]


    return device_info
