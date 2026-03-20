import secrets
from datetime import timedelta
from django.utils import timezone
from django.db import models


class User(models.Model):
    username = models.CharField(max_length=100, unique=True)
    email = models.EmailField(unique=True)
    password = models.CharField()

    is_email_confired = models.BooleanField(default=False)
    email_confirm_token = models.CharField(default='')
    email_confirm_at = models.DateTimeField(blank=True, null=True)

    reset_password_token = models.CharField(default='')
    reset_password_at = models.DateTimeField(null=True, blank=True)

    def generate_email_token(self):
        self.email_confirm_token = secrets.token_urlsafe(8)
        self.email_confirm_at = timezone.now()
        self.save()
        return self.email_confirm_token

    def confirm_email(self):
        self.is_email_confired = True
        self.email_confirm_token = ''
        self.email_confirm_at = None
        self.save()

    def email_confirm_validate(self):
        if self.is_email_confired:
            return False
        if not self.email_confirm_at:
           return False
        return timezone.now() <= self.email_confirm_at + timedelta(minutes=3)

    def email_send_validate(self):
        if self.is_email_confired:
            return False
        if not self.email_confirm_at:
           return True

        return timezone.now() > self.email_confirm_at + timedelta(minutes=3)

    def generate_reset_password_token(self):
       self.reset_password_token = secrets.token_urlsafe(8)
       self.reset_password_at = timezone.now()
       self.save()
       return self.reset_password_token

    def clear_reset_password(self):
       self.reset_password_at = None
       self.reset_password_token = ''
       self.save()

    def reset_password_confirm(self):
       if not self.reset_password_token or not self.reset_password_at:
          return False
       return timezone.now() <= self.reset_password_at + timedelta(minutes=3)

    def reset_password_send(self):
       if not self.reset_password_at:
          return False
       return timezone.now() > self.reset_password_at + timedelta(minutes=3)
