from Main.Modules import EmailServices
from TicketDais.settings import EMAIL_HOST, EMAIL_HOST_PASSWORD

# class EmailVerification:
email_verification = EmailServices.EmailVerification(EMAIL_HOST, EMAIL_HOST_PASSWORD, length=6)


def send_otp(request, email):
    msg = open("./Main/Modules/EmailTemplate/verify_email.html").read()
    email_verification.send_otp(email, "TicketDais - Verification", "TicketDais - Verification", "OTP For TicketDais",
                                msg)


def verify_otp(self):
    pass
