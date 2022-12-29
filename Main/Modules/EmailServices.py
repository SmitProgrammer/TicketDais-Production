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
        """EmailVerification class for sending and verifying OTP
        :param source_mail: The email from which the OTP will be sent
        :param psw: The password of the email from which the OTP will be sent
        :param trys: The number of tries the user has to enter the correct OTP
        :param length: The length of the OTP
        """
        self.otp = ""
        self.verified = False
        self.psw = psw
        self.trys = trys
        self.email_status = False
        self.length = length
        self.source_mail = source_mail

    # @staticmethod # This is a static method, so you don't need to create an object to use it
    def send_otp(self, destination_mail, source_title, destination_title, mail_subject, mail_body):
        """This method sends the OTP to the destination mail
        :param destination_mail: The email to which the OTP will be sent
        :param source_title: The title of the source email
        :param destination_title: The title of the destination email
        :param mail_subject: The subject of the mail
        :param mail_body: The body of the mail
        :return: True if the mail is sent successfully, Error if the mail is not sent
        """
        send_email = SendMail(self.source_mail, self.psw)
        self.otp = str(random.randint(int("0" * self.length), int("9" * self.length)))
        mail_body = mail_body.replace(r"{OTP}", self.otp)
        # print(mail_body)
        self.email_status = send_email.send(source_title, destination_title, destination_mail, mail_subject, mail_body)
        return self.email_status

    def verify_otp(self, otp):
        """This method verifies the OTP
        :param otp: The OTP entered by the user
        :return: True if the OTP is correct, False if the OTP is incorrect, MaxTryReached if the user has exceeded the maximum number of tries
        """
        if self.trys > 0:
            if str(otp) == str(self.otp):
                self.verified = True
                return True
            self.trys -= 1
            return False
        else:
            raise MaxTryReached("Maximum Try Reached")


class SendMail:
    source_email = ""
    source_pass = ""

    def __init__(self, source_email, source_pass):
        """SendMail class for sending emails
        :param source_email: The email from which the email will be sent
        :param source_pass: The password of the email from which the email will be sent
        """
        self.source_email = source_email
        self.source_pass = source_pass

    def send(self, source_title, destination_title, destination_mail, subject, text):
        """This method sends the email
        :param source_title: The title of the source email
        :param destination_title: The title of the destination email
        :param destination_mail: The email to which the email will be sent
        :param subject: The subject of the email
        :param text: The body of the email
        :return: True if the email is sent successfully, Error if the email is not sent
        """
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
