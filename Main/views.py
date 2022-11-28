import json
import os.path
import pyrebase
from django.contrib import messages
from django.shortcuts import render, redirect
import geocoder
from Main.Modules import helper, EmailServices

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
    try:
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
    except Exception as e:
        print(e)
        return False


def index(request):
    user = request.session.get('id')
    if user is not None:
        try:
            user = auth.get_account_info(user)
            auth.refresh(auth.current_user['refreshToken'])
        except Exception as e:
            print(e)
        print(auth.current_user)
    if not os.path.exists("tmp"):
        os.makedirs("tmp")
    ip = geocoder.ip('me')
    print(ip.city)
    print(ip.latlng)
    # helper.SendEmailVerification("smittalsaniya38@gmail.com")
    return render(request, 'index.html')


def login(request):
    user = None
    if request.method == "POST" and 'email' in request.POST and 'password' in request.POST:
        try:
            user = auth.sign_in_with_email_and_password(email=request.POST['email'], password=request.POST['password'])
            print(user)
            request.session['id'] = user['idToken']
            request.session['userId'] = user['localId']
            user = helper.get_user_info(user, db)
            print(user)
            return render(request, "verify_2fa.html")
            # return redirect("/")
        except Exception as e:
            print(e)
            if "INVALID_PASSWORD" or "EMAIL_NOT_FOUND" in str(e):
                messages.warning(request, "Invalid email or password")
                return redirect('/login')
        # print(user)
    elif request.method == "POST" and request.POST['data'] is not None:
        print("2fa-" * 40)
        user = dict(auth.get_account_info(request.session.get('id'))['users'])
        print(user)
        helper.verify_user(request.session.get('id'), db)
        print(request.session.get('userId'))
        if request.POST.get('otp') == helper.get_2fa_otp(request, db):
            messages.success(request, "Login success!")
            return redirect("/")
        else:
            messages.warning(request, "Wrong OTP Please try again")
            return render(request, "verify_2fa.html")
        # return HttpResponse(helper.get_2fa_otp(request, db))
    elif request.POST.get('email') == "" or request.POST.get('password') == "":
        messages.warning(request, "Email ID or Password cannot be empty")
        return render(request, 'login.html')
    else:
        return render(request, 'login.html')


def register(request):
    if request.method == "POST":
        try:
            if os.path.exists("tmp/" + auth.current_user['email']):
                created = True
        except:
            created = False
    print(request.method)
    if validate(request):
        try:
            if not os.path.exists(request.POST['email']):
                user = auth.create_user_with_email_and_password(email=request.POST['email'],
                                                                password=request.POST['password'])
                print(user)
                user['displayName'] = request.POST['name']
                user['phoneNum'] = request.POST['phone']
                MFA = helper.get_2fa(user)
                user['2fa'] = MFA[0]
                user['2fa_img'] = MFA[1]
                helper.create_user(user, db, MFA[0])
                with open("tmp/" + request.POST['email'], "w") as data:
                    json.dump(user, data)
                created = True
        except Exception as e:
            if "EMAIL_EXISTS" in str(e):
                print(e)
                messages.warning(request, "Email ID already registered")
            elif os.path.exists("tmp/" + request.POST['email']):
                with open("tmp/" + request.POST['email']) as data:
                    user = json.load(data)
                helper.delete_user(user, db, auth)
                messages.warning(request, "Something Went Wrong!")
        finally:
            if created:
                if request.method == "POST" and request.POST['form'] == "1":
                    helper.send_email_verification(request.POST['email'])
                    messages.success(request, f"OTP Sent on {request.POST['email']}")
                    return render(request, 'signup.html', {'verify': True, 'email': request.POST['email']})
            else:
                print("Refresh")
                if os.path.exists("tmp/" + request.POST['email']):
                    with open("tmp/" + request.POST['email']) as data:
                        user = json.load(data)
                    helper.delete_user(user, db, auth)
                    os.remove("tmp/" + request.POST['email'])
                return redirect('/register')
    elif request.method == "POST":
        try:
            with open("tmp/" + request.POST['email']) as data:
                user = json.load(data)
            MFA = [user['2fa'], user['2fa_img']]
            try:
                # try:
                #     if request.POST['resend']:
                #         helper.send_email_verification(request.POST['email'])
                #         messages.success(request, "OTP sent")
                #         return render(request, 'signup.html', {'verify': True, 'email': request.POST['email']})
                # except Exception as e:
                print(f"Entered OTP {request.POST['otp']}")
                if helper.verify_email(request.POST['otp']):
                    # helper.create_user_vault(user, db, MFA[0])
                    return render(request, 'signup.html',
                                  {'img': MFA[1], 'code': MFA[0], 'MFA': True, 'email': user['email']})
                else:
                    messages.warning(request, "Invalid OTP")
                    return render(request, 'signup.html', {'verify': True, 'email': user['email']})
            except EmailServices.MaxTryReached:
                messages.warning(request, "You have entered wrong otp 3 times")
                return redirect("/")
            except Exception as e:
                print(e)
                if request.POST['check'] == "done":
                    messages.success(request=request, message="Account Created")
                    os.remove("tmp/" + request.POST['email'])
                    return redirect("/")
        except Exception as e:
            print(e)
            helper.delete_user(user, db, auth)
            messages.warning(request, "Something went wrong!")
            return render(request, 'signup.html')
    else:
        return render(request, 'signup.html')


def forgot_psw(request):
    if request.method == "POST":
        if not request.POST['email'] == "":
            try:
                auth.send_password_reset_email(request.POST['email'])
                messages.success(request=request, message="Password Reset Link Has Been Sent To Your Email Address")
            except Exception as e:
                if "EMAIL_NOT_FOUND" in str(e):
                    messages.warning(request, "Email Not Found!")
                else:
                    messages.warning(request, "Something Went Wrong!")
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


def about(request):
    return render(request, 'about.html')


def contact(request):
    return render(request, 'contact.html')
