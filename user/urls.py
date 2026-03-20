from django.urls import path
from .views import *

urlpatterns = [
    path('register/', register, name='register'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('', profile, name='profile'),
    path('confirm-email/<str:token>/', confirm_email, name='confirm_email'),
    path('reset-password/', reset_password_request, name='reset_password'),
    path('reset-password/<str:token>/', reset_password_confirm, name='reset_password_confirm'),
    path('change-password/', change_password, name='change_password'),
]