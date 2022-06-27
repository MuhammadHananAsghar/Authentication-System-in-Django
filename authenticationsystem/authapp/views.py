# Essentials Imports
from django.contrib.sites.shortcuts import get_current_site
from email.mime.multipart import MIMEMultipart
from django.shortcuts import render, redirect
from datetime import timedelta
from django.views.generic import View
from email.mime.text import MIMEText
from django.http import HttpResponse
from django.utils import timezone
from dotenv import load_dotenv
import hashlib
import smtplib
import random
import os


# Models Imports
from .models import Verify
from .models import Users


# Loading .env file
load_dotenv()


# Enviroment Variables
EMAIL_USE_TLS = os.getenv('EMAIL_USE_TLS')
EMAIL_HOST = os.getenv('EMAIL_HOST')
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')
EMAIL_PORT = os.getenv('EMAIL_PORT')


# Globals
context = {"email": "", "password": "", "error": ""}
status = {"status": ""}
user_email = None


class Login(View):
    template_name = "login.html"

    def md5hasher(self, what_text):       
        return hashlib.md5(what_text.encode("utf")).hexdigest()

    def get(self, request, *args, **kwargs):
        if request.session.get("has_logged", None):
            return redirect("/dashboard")
        return render(request, self.template_name, status)


    def post(self, request, *args, **kwargs):
        user_email = request.POST['user_email']
        user_password = request.POST['user_password']

        try:
            comment = Users.objects.get(email=user_email).email
        except Users.DoesNotExist:
            comment = None

        if comment:
            time = Verify.objects.get(email = user_email).time
            email = Users.objects.get(email = user_email).email
            active = Users.objects.get(email = user_email).active
            password = Users.objects.get(email = user_email).password
            if (timezone.now() < time) and (active == 0):
                return HttpResponse("We have send you a activation email. please activate your account.")
            if email == user_email:
                if password == self.md5hasher(user_password):
                    request.session["has_logged"] = True
                    request.session["user_email"] = user_email
                    return redirect("/dashboard")
                else:
                    return HttpResponse("Password is incorrect.")
        else:
            request.session["has_logged"] = False
            return HttpResponse("User is not present.")


class Registration(View):
    template_name = "registration.html"

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, context)


class PasswordReset(View):
    template_name = "passwordreset.html"

    def md5hasher(self, what_text):       
        return hashlib.md5(what_text.encode("utf")).hexdigest()

    def get(self, request, *args, **kwargs):
        if request.session.get("has_logged", None):
            return render(request, self.template_name)
        return redirect("/")


    def post(self, request, *args, **kwargs):
        user_email = request.session["user_email"]
        user_password = request.POST['user_password']
        confirm_user_password = request.POST['confirm_user_password']
        if user_password == confirm_user_password:
            if (len(user_password) > 5) and (len(user_password) < 20):
                Users.objects.filter(email=user_email).update(password=self.md5hasher(user_password))    
                return HttpResponse("Password changes.")
            return HttpResponse("Password must be in between 5-20.")
        return HttpResponse("Password and confirm password both must be same.")


class Logout(View):
    def get(self, request, *args, **kwargs):
        request.session["has_logged"] = False
        return redirect("/")


class Verification(View):
    template_name = "verification.html"

    def get(self, request, *args, **kwargs):
        global user_email
        user_email = kwargs.get("email")
        return render(request, self.template_name)

    def post(self, request, *args, **kwargs):
        global user_email
        token_id = request.POST['verification_code']
        try:
            comment = Users.objects.get(email=user_email).email
        except Users.DoesNotExist:
            comment = None

        if comment:
            if Users.objects.get(email=user_email).active == 1:
                return HttpResponse("User is already registerd and verified.")
            else:
                status["status"] = ""
                token = Verify.objects.get(email = user_email).token
                time = Verify.objects.get(email = user_email).time
                active = Users.objects.get(email = user_email).active
                if (time > timezone.now()) and (active == 0):
                    if token == token_id:
                        Users.objects.filter(email = user_email).update(active=True)
                        user_email = None
                    else:
                        return HttpResponse("Token is invalid.")
                else:
                    if active == 1:
                        return HttpResponse("You have already verified your account.")
                    else:
                        Verify.objects.filter(email = user_email).delete()
                        Users.objects.filter(email = user_email).delete()
                        return HttpResponse("Link is Expired.")
        else:
            return HttpResponse("User does not present.")

        return redirect("/")


class CreateUser(View):
    cond = False

    def token_generator(self):
        token = ""
        nums = [i for i in range(10)]
        for _ in range(10):
            token += str(random.choice(nums))
        return token

    def md5hasher(self, what_text):       
        return hashlib.md5(what_text.encode("utf")).hexdigest()

    def send_email(self, url, token, email):
        mail_content = f'''
        This verification code is only valid for 5 minutes.

        Verification Code: {token}

        Copy this url in browser:
        http://{url}/verify/{email}
        '''

        # Setup the MIME
        message = MIMEMultipart()
        message['From'] = EMAIL_HOST_USER
        message['To'] = email
        message['Subject'] = 'Verificaion Email - Muhammad Hanan Asghar'

        session = smtplib.SMTP(EMAIL_HOST, EMAIL_PORT)
        session.ehlo()
        session.starttls()
        session.ehlo()
        session.login(EMAIL_HOST_USER, EMAIL_HOST_PASSWORD)

        message.attach(MIMEText(mail_content, 'plain'))
        text = message.as_string()
        session.sendmail(EMAIL_HOST_USER, email, text)
        session.quit()
        print('Mail Sent')

    def get(self, request, *args, **kwargs):
        return HttpResponse("Don't Accpet Get Request")

    def post(self, request, *args, **kwargs):
        global context, status
        form = request.POST
        user_name = form['user_name']
        user_email = form['user_email']
        user_password = form['user_password']
        user_age = form['user_age']
        user_bio = form['user_bio']
        user_job = form['user_job']
        user_interest = str(form.get('user_interest', ''))

        try:
            try:
                comment = Users.objects.get(email=user_email).email
            except Users.DoesNotExist:
                comment = None
            if comment:
                context['email'] = "User already presnet."
            else:
                context['email'] = ""
                if (len(user_password) > 5) and (len(user_password) < 20):
                    # to get the domain of the current site
                    current_site = get_current_site(request)

                    # Saving User Details
                    object = Users.objects.create(
                        name=user_name,
                        email=user_email,
                        password=self.md5hasher(user_password),
                        age=user_age,
                        biography=user_bio,
                        job_role=user_job,
                        interest=user_interest
                    )
                    object.save()

                    # Verification Details
                    five_mins = timezone.now() + timedelta(minutes=5)
                    _token = self.token_generator()
                    verify = Verify.objects.create(
                        token= _token,
                        email=user_email,
                        time=five_mins
                    )
                    verify.save()
                    self.send_email(current_site, _token, user_email)

                    self.cond = True
                    context["password"] = ""
                    status["status"] = "We have send you a confirmation email."
                else:
                    status["status"] = ""
                    context["password"] = "Password must be in between 5-20 characters."
        except Exception as e:
            print(e)
            context['error'] = "Error in the server right know."
            self.cond = False

        if self.cond:
            return redirect("/")

        return redirect("/register")


class Dashboard(View):
    template_name = "main.html"

    def get(self, request, *args, **kwargs):
        if request.session.get("has_logged", None):
            return render(request, self.template_name)
        return redirect("/")