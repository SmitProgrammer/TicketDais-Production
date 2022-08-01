import pyrebase
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
print(auth.current_user)
user_login = auth.sign_in_with_email_and_password(input("Enter Email: "), input("Enter Psw: "))