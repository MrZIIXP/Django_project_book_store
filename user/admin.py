from django.contrib import admin
from .models import User
@admin.register(User)
class UserAdmin(admin.ModelAdmin):
   list_display = ['username', 'email', 'is_email_confired', 'email_confirm_token']