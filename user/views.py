from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from django.contrib.auth.hashers import make_password, check_password
from .models import User
import datetime


# --- Register ---
def register(request):
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '').strip()
        confirm_password = request.POST.get('confirm_password', '').strip()

        if not username or not email or not password or not confirm_password:
            messages.error(request, "All fields are required.")
            return redirect('register')

        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return redirect('register')

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already exists.")
            return redirect('register')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return redirect('register')

        hashed_password = make_password(password)
        user = User.objects.create(username=username, email=email, password=hashed_password)
        token = user.generate_email_token()
        user.save()

        # Send email
        link = request.build_absolute_uri(f"/account/confirm-email/{token}/")
        send_mail(
            subject="Confirm your email",
            message=f"Click to confirm: {link}",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
        )
        messages.success(request, "Registered! Check email to confirm.")
        return redirect('login')

    return render(request, 'register.html')


# --- Confirm Email ---
def confirm_email(request, token):
    user = get_object_or_404(User, email_confirm_token=token)
    if user.email_confirm_validate():
        user.confirm_email()
        user.save()
        messages.success(request, "Email confirmed! You can login now.")
        return redirect('login')
    messages.error(request, "Invalid or expired token.")
    return redirect('login')


# --- Login ---
def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '').strip()
        user = User.objects.filter(email=email).first()
        if not user:
            messages.error(request, "User not found.")
            return redirect('login')
        if not user.is_email_confired:
            if user.email_send_validate():
               token = user.generate_email_token()
               link = request.build_absolute_uri(f"/account/confirm-email/{token}/")
               send_mail(
                     subject="Confirm your email",
                     message=f"Click to confirm: {link}",
                     from_email=settings.DEFAULT_FROM_EMAIL,
                     recipient_list=[email],
               )
               
               messages.error(request, "Email not confirmed. We send new link")
            else:
               last_time = user.email_confirm_at + datetime.timedelta(minutes=3)
               messages.error(request, f"Email not confirmed. Wait {last_time - timezone.now()}")
            return redirect('login')
        if not check_password(password, user.password):
            messages.error(request, "Incorrect password.")
            return redirect('login')

        request.session['user'] = {'id': user.id, 'username': user.username}
        messages.success(request, "Logged in successfully!")
        return redirect('profile')

    return render(request, 'login.html')


# --- Profile ---
def profile(request):
    user_session = request.session.get('user')
    if not user_session:
        messages.error(request, "Login required.")
        return redirect('login')
    user = get_object_or_404(User, id=user_session['id'])
    return render(request, 'profile.html', {'user': user})


# --- Logout ---
def logout_view(request):
    request.session.flush()
    messages.success(request, "Logged out successfully!")
    return redirect('login')


def reset_password_request(request):
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        user = User.objects.filter(email=email).first()
        if user:
            user.generate_reset_password_token()
            user.save()
            link = request.build_absolute_uri(f"/account/reset-password/{user.reset_password_token}/")
            send_mail(
                "Reset your password",
                f"Click to reset: {link}",
                settings.DEFAULT_FROM_EMAIL,
                [email]
            )
        messages.success(request, "If email exists, reset link sent.")
        return redirect('login')
    return render(request, 'reset_password_request.html')


# --- Reset Password Step 2 ---
def reset_password_confirm(request, token):
    user = User.objects.filter(reset_password_token=token).first()
    if not user or not user.reset_password_confirm():
        messages.error(request, "Invalid or expired token.")
        return redirect('login')

    if request.method == 'POST':
        password = request.POST.get('password', '').strip()
        confirm_password = request.POST.get('confirm_password', '').strip()
        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return redirect(f'/account/reset-password/{token}/')
        user.password = make_password(password)
        user.clear_reset_password()
        user.save()
        messages.success(request, "Password reset successfully!")
        return redirect('login')

    return render(request, 'reset_password_confirm.html', {'token': token})


# --- Change Password ---
def change_password(request):
    user_session = request.session.get('user')
    if not user_session:
        messages.error(request, "Login required.")
        return redirect('login')
    user = get_object_or_404(User, id=user_session['id'])

    if request.method == 'POST':
        old_password = request.POST.get('old_password', '').strip()
        new_password = request.POST.get('new_password', '').strip()
        confirm_password = request.POST.get('confirm_password', '').strip()

        if not check_password(old_password, user.password):
            messages.error(request, "Old password incorrect.")
            return redirect('change_password')

        if new_password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return redirect('change_password')

        user.password = make_password(new_password)
        user.save()
        messages.success(request, "Password changed successfully!")
        return redirect('profile')

    return render(request, 'change_password.html')