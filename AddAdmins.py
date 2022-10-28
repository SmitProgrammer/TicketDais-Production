
import pyrebase
import getpass
from Main.Modules import EmailServices
from Main.Modules.EmailServices import EmailVerification

firebaseConfig = {
  "apiKey": "AIzaSyCdewMnKCWYeaAyEQ8o_DpJNT9MFArZ5rI",
  "authDomain": "ticketdais.firebaseapp.com",
  "databaseURL": "https://ticketdais-default-rtdb.firebaseio.com",
  "projectId": "ticketdais",
  "storageBucket": "ticketdais.appspot.com",
  "messagingSenderId": "94691421849",
  "appId": "1:94691421849:web:896ce2c62f8e707a14d208",
  "measurementId": "G-DJY7Z3HWNW"
}
firebase = pyrebase.initialize_app(firebaseConfig)
auth = firebase.auth()
db = firebase.database()
# print(auth.current_user)
admins = []
for i in range(int(input("How many admin you want ? "))):
    email = input("Enter Email: ")
    psw = getpass.getpass("Enter Password: ")
    print("Connecting to server...")
    # auth.send_email_verification(user_login['idToken'])
    with open('cred.txt', 'r') as cred:
      cred = (cred.readline()).split(":")
    Email_Verification = EmailVerification(source_mail=cred[0], psw=cred[1])
    source_title = "TicketDais"
    destination_title = ""
    destination_mail = email
    subject = "Verification From TicketDais"
    text = """<b>Hello,
    This is an important mail from TicketDais Admin
    Your Admin Registration Process Has Been Started 
    and to complete your admin registration
    Enter this otp
    <h1>{OTP}</h1></b>"""
    print("Sending OTP to  " + email)
    Email_Verification.send_otp(source_title=source_title, destination_title=destination_title, destination_mail=destination_mail, mail_subject=subject, mail_body=text)
    print("OTP sent on  " + email if Email_Verification.email_status is True else "Something went wrong\n " +Email_Verification.email_status)
    verification = False
    while True:
        try:
            if Email_Verification.verify_otp(input("Enter OTP: ")):
                print("Email Verified")
                verification = True
                break
            else:
                print("Verification Failed\nUnable To Create Admin")
                verification = False
        except EmailServices.MaxTryReached:
            print("Email Verification Failed")
            verification = False
            break
    if not verification:
        continue
    else:
        print("Creating user...")
        user_login = auth.create_user_with_email_and_password(email, psw)
        print("Adding user into database...")
        data = {
          "users/ " +user_login["localId"]: {
            "email_id": email,
            "name": input("Enter Your name: "),
            "balance": 100,
            "email_verified": verification,
            "phone_no": input("Enter your phone number: "),
            "banned": False,
            "profile": "",
            "tickets" :{
                "bus" :{},
                "train" :{},
                "flight" :{},
            }
          }
        }
        db.update(data)
        admins.append(user_login["localId"]+":"+email)
        print(f"{email} is successfully added")
for admin in admins:
    print(admin)
    # admin = admin.split()
    # print(f"Email: {admin[1]}\nUID: {admin[0]}\n\n")