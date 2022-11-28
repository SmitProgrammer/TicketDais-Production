import random
import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


class MaxTryReached(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return (repr(self.value))


class EmailVerification():
    def __init__(self, source_mail, psw, trys=3, length=4):
        self.otp = ""
        self.verified = False
        self.psw = psw
        self.trys = trys
        self.email_status = False
        self.length = length
        self.source_mail = source_mail

    # @property
    def send_otp(self, destination_mail, source_title, destination_title, mail_subject, mail_body):
        send_email = SendMail(self.source_mail, self.psw)
        self.otp = str(random.randint(int("0" * self.length), int("9" * self.length)))
        mail_body = mail_body.replace(r"{OTP}", self.otp)
        # print(mail_body)
        self.email_status = send_email.send(source_title, destination_title, destination_mail, mail_subject, mail_body)

    def verify_otp(self, otp):
        if self.trys > 0:
            if str(otp) == str(self.otp):
                self.verified = True
                return True
            else:
                self.trys -= 1
                return False
        else:
            raise MaxTryReached("Maximum Try Reached")


class SendMail:
    source_email = ""
    source_pass = ""

    def __init__(self, source_email, source_pass):
        self.source_email = source_email
        self.source_pass = source_pass

    def send(self, source_title, destination_title, destination_mail, subject, text):
        message = MIMEMultipart('alternative')
        message["Subject"] = subject
        message["From"] = f"{source_title} <{self.source_email}>"
        message["To"] = f"{destination_title} <{destination_mail}>"
        message.attach(MIMEText(text, "html"))
        context = ssl.create_default_context()
        try:
            with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
                server.login(self.source_email, self.source_pass)
                server.sendmail(
                    self.source_email, destination_mail, message.as_string()
                )
                return True
        except Exception as e:
            return e
