import geocoder
import pyrebase
from django.contrib import messages
from django.http import HttpResponse
# from django.contrib.gis.geoip2 import GeoIP2
from django.shortcuts import render, redirect

from Main.Modules import helper

# Create your views here.
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


def validate(request):
    if request.method == "POST":
        name = request.POST['name']
        email = request.POST['email']
        psw = request.POST['password']
        c_psw = request.POST['confirm_password']
        phone = request.POST['phone']
        if name == "" or email == "" or phone == "" or psw == "" or c_psw == "":
            messages.warning(request, "Please Fill All Details")
        elif not psw == c_psw:
            messages.warning(request=request, message="Password not matched ")
        elif len(phone) > 10:
            messages.warning(request, "Invalid Phone Number")
        elif not "@" in email:
            messages.warning(request, "Invalid Email ID")
        else:
            return True
    else:
        return False


def index(request):
    # print(get_client_ip(request))
    # ip = geocoder.ip(get_client_ip(request)[0])
    ip = geocoder.ip('me')
    print(ip.city)
    print(ip.latlng)
    return render(request, 'index.html')


def login(request):
    # if validate(request):
    if request.method == "POST":
        user = auth.sign_in_with_email_and_password(email=request.POST['email'], password=request.POST['password'])

    # else:
    #     pass
    return render(request, 'login.html')


def register(request):
    print(request.method)
    # messages.success(request=request, message="Account Created")
    # if request.method == "POST":
    #     name = request.POST['name']
    #     email = request.POST['email']
    #     psw = request.POST['password']
    #     c_psw = request.POST['confirm_password']
    #     phone = request.POST['phone']
    #     if name == "" or email == "" or phone == "" or psw == "" or c_psw == "":
    #         messages.warning(request, "Please Fill All Details")
    #     elif not psw == c_psw:
    #         messages.warning(request=request, message="Password not matched ")
    #     elif len(phone) > 10:
    #         messages.warning(request, "Invalid Phone Number")
    #     elif not "@" in email:
    #         messages.warning(request, "Invalid Email ID")
    #     else:
    if validate(request):
        user = auth.create_user_with_email_and_password(email=request.POST['email'], password=request.POST['password'])
        print(user)
        user['displayName'] = request.POST['name']
        user['phoneNum'] = request.POST['phone']
        helper.CreateUser(user, db)
        messages.success(request=request, message="Account Created")
        return render(request, 'signup.html')
    else:
        return render(request, 'signup.html')


def forgot_psw(request):
    if request.method == "POST":
        if not request.POST['email'] == "":
            messages.success(request=request, message="Password Reset Link Has Been Sent To Your Email Address")
            return redirect("/")
        else:
            messages.warning(request, "Please Enter Your Email Address!")
            return render(request, 'forgot_psw.html')
    else:
        return render(request, 'forgot_psw.html')


def edit(request):
    if request.GET['mode'] == "resetPassword":
        try:
            print(request.GET['mode'])
            print(request.GET["oobCode"])
            messages.success(request, "Password Reset done")
        except:
            messages.warning(request, "Unable to reset")
    else:
        messages.warning(request, "Something went wrong!")
    return redirect(request, '/')

