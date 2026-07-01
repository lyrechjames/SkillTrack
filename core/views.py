import re

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.cache import cache
from django.core.mail import send_mail
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.http import JsonResponse
from django.shortcuts import render, redirect


LOCKOUT_LIMIT = 5
LOCKOUT_SECONDS = 15 * 60
PASSWORD_PATTERN = re.compile(r'^(?=.*[A-Z])(?=.*\d)(?=.*[^A-Za-z0-9]).{8,}$')


def _normalize_email(email):
    return (email or '').strip().lower()


def _lockout_key(email):
    return f'login-lockout:{email}'


def _attempt_key(email):
    return f'login-attempts:{email}'


def _valid_email(email):
    try:
        validate_email(email)
    except ValidationError:
        return False
    return True


def register_view(request):
    if request.method == 'POST':
        full_name = (request.POST.get('full_name') or '').strip()
        email = _normalize_email(request.POST.get('email'))
        password = request.POST.get('password') or ''
        confirm_password = request.POST.get('confirm_password') or ''
        accepted_terms = request.POST.get('terms') == 'on'

        context = {'full_name': full_name, 'email': email}

        if not full_name or not email or not password or not confirm_password:
            messages.error(request, "All fields are required.")
            return render(request, 'core/register.html', context)

        if not _valid_email(email):
            messages.error(request, "Enter a valid email address.")
            return render(request, 'core/register.html', context)

        if not PASSWORD_PATTERN.match(password):
            messages.error(
                request,
                "Password must be at least 8 characters and include 1 uppercase letter, 1 number, and 1 special character."
            )
            return render(request, 'core/register.html', context)

        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return render(request, 'core/register.html', context)

        if not accepted_terms:
            messages.error(request, "You must agree to the Terms & Conditions.")
            return render(request, 'core/register.html', context)

        if User.objects.filter(username=email).exists() or User.objects.filter(email=email).exists():
            messages.error(request, "This email address is already registered. Did you forget your password?")
            return render(request, 'core/register.html', context)

        name_parts = full_name.split(maxsplit=1)
        user = User.objects.create_user(username=email, email=email, password=password)
        user.first_name = name_parts[0]
        user.last_name = name_parts[1] if len(name_parts) > 1 else ''
        user.save()

        send_mail(
            subject='Verify your account',
            message='Account created successfully! Please check your email to verify your account.',
            from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', None),
            recipient_list=[email],
            fail_silently=True,
        )
        messages.success(request, "Account created successfully! Please check your email to verify your account.")
        return redirect('login')

    return render(request, 'core/register.html')


def login_view(request):
    if request.method == 'POST':
        email = _normalize_email(request.POST.get('email'))
        password = request.POST.get('password') or ''
        remember_me = request.POST.get('remember_me') == 'on'

        if not email or not password or not _valid_email(email):
            messages.error(request, "Incorrect email or password. Please try again.")
            return render(request, 'core/login.html', {'email': email})

        if cache.get(_lockout_key(email)):
            messages.error(
                request,
                "Account temporarily locked due to too many failed attempts. Please try again in 15 minutes."
            )
            return render(request, 'core/login.html', {'email': email})

        user = authenticate(request, username=email, password=password)

        if user is not None:
            cache.delete(_attempt_key(email))
            cache.delete(_lockout_key(email))
            login(request, user)
            if not remember_me:
                request.session.set_expiry(0)
            else:
                request.session.set_expiry(60 * 60 * 24 * 14)
            messages.success(request, "Login successful! Redirecting to your dashboard...")
            return redirect('dashboard')

        attempts = cache.get(_attempt_key(email), 0) + 1
        cache.set(_attempt_key(email), attempts, LOCKOUT_SECONDS)
        if attempts >= LOCKOUT_LIMIT:
            cache.set(_lockout_key(email), True, LOCKOUT_SECONDS)
            messages.error(
                request,
                "Account temporarily locked due to too many failed attempts. Please try again in 15 minutes."
            )
        else:
            messages.error(request, "Incorrect email or password. Please try again.")

    return render(request, 'core/login.html')


def login_view_alt(request):
    if request.method == 'POST':
        email = _normalize_email(request.POST.get('email'))
        password = request.POST.get('password') or ''
        remember_me = request.POST.get('remember_me') == 'on'

        if not email or not password or not _valid_email(email):
            messages.error(request, "Incorrect email or password. Please try again.")
            return render(request, 'core/login_alt.html', {'email': email})

        if cache.get(_lockout_key(email)):
            messages.error(
                request,
                "Account temporarily locked due to too many failed attempts. Please try again in 15 minutes."
            )
            return render(request, 'core/login_alt.html', {'email': email})

        user = authenticate(request, username=email, password=password)

        if user is not None:
            cache.delete(_attempt_key(email))
            cache.delete(_lockout_key(email))
            login(request, user)
            if not remember_me:
                request.session.set_expiry(0)
            else:
                request.session.set_expiry(60 * 60 * 24 * 14)
            messages.success(request, "Login successful! Redirecting to your dashboard...")
            return redirect('dashboard')

        attempts = cache.get(_attempt_key(email), 0) + 1
        cache.set(_attempt_key(email), attempts, LOCKOUT_SECONDS)
        if attempts >= LOCKOUT_LIMIT:
            cache.set(_lockout_key(email), True, LOCKOUT_SECONDS)
            messages.error(
                request,
                "Account temporarily locked due to too many failed attempts. Please try again in 15 minutes."
            )
        else:
            messages.error(request, "Incorrect email or password. Please try again.")

    return render(request, 'core/login_alt.html')


@login_required(login_url='login')
def dashboard_view(request):
    return render(request, 'core/dashboard.html', _dashboard_payload())


@login_required(login_url='login')
def dashboard_metrics_view(request):
    return JsonResponse(_dashboard_payload())


def logout_view(request):
    logout(request)
    messages.success(request, "You have been securely logged out. See you next time!")
    return redirect('login')


def _dashboard_payload():
    return {
        'metrics': {
            'total_sales': '$12,450',
            'active_users': '3,421',
            'tasks': '18',
            'notifications': 3,
        },
        'activities': [
            'User J.D. updated profile setting',
            'User M.K. completed system onboarding check',
            'Finance report refreshed successfully',
        ],
    }
