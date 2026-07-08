import re
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.cache import cache
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse

from .models import UserSkill, JobApplication, AdminLog
from .forms import UserRegisterForm, UserSkillForm, JobApplicationForm, UserProfileForm

User = get_user_model()

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


def log_action(user, action_flag, change_message):
    """Utility to create an AdminLog entry for audits"""
    AdminLog.objects.create(
        user=user if (user and user.is_authenticated) else None,
        action_flag=action_flag,
        change_message=change_message
    )


# --- AUTHENTICATION VIEWS ---

def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
        
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, "Account created successfully! You can now log in.")
            log_action(user, 'ADD', f"New user registered: {user.username} (Email: {user.email})")
            return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, 'core/register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        email = _normalize_email(request.POST.get('email'))
        password = request.POST.get('password') or ''
        remember_me = request.POST.get('remember_me') == 'on'

        if not email or not password or not _valid_email(email):
            messages.error(request, "Incorrect email or password. Please try again.")
            return render(request, 'core/login.html', {'email': email})

        # Lockout check
        if cache.get(_lockout_key(email)):
            messages.error(
                request,
                "Account temporarily locked due to too many failed attempts. Please try again in 15 minutes."
            )
            return render(request, 'core/login.html', {'email': email})

        # Custom auth using email as username
        user = authenticate(request, username=email, password=password)

        if user is not None:
            cache.delete(_attempt_key(email))
            cache.delete(_lockout_key(email))
            login(request, user)
            if not remember_me:
                request.session.set_expiry(0)
            else:
                request.session.set_expiry(60 * 60 * 24 * 14)
            messages.success(request, "Login successful!")
            log_action(user, 'EDIT', f"User logged in: {user.username}")
            return redirect('dashboard')

        # Authentication failed
        attempts = cache.get(_attempt_key(email), 0) + 1
        cache.set(_attempt_key(email), attempts, LOCKOUT_SECONDS)
        if attempts >= LOCKOUT_LIMIT:
            cache.set(_lockout_key(email), True, LOCKOUT_SECONDS)
            log_action(None, 'EDIT', f"Account lockout triggered for email: {email}")
            messages.error(
                request,
                "Account temporarily locked due to too many failed attempts. Please try again in 15 minutes."
            )
        else:
            messages.error(request, "Incorrect email or password. Please try again.")

    return render(request, 'core/login.html')


def login_view_alt(request):
    """Alternate login view matching the config urls"""
    return login_view(request)


def logout_view(request):
    if request.user.is_authenticated:
        log_action(request.user, 'EDIT', f"User logged out: {request.user.username}")
    logout(request)
    messages.success(request, "You have been securely logged out.")
    return redirect('login')


# --- DASHBOARD & METRICS VIEWS ---

@login_required(login_url='login')
def dashboard_view(request):
    user = request.user
    
    if user.is_staff or user.is_superuser:
        # --- STAFF / ADMIN DASHBOARD ---
        total_users = User.objects.count()
        total_skills = UserSkill.objects.count()
        total_applications = JobApplication.objects.count()
        total_logs = AdminLog.objects.count()
        
        users_list = User.objects.all().order_by('-date_joined')[:10]
        recent_logs = AdminLog.objects.all().order_by('-action_time')[:15]
        
        context = {
            'is_staff': True,
            'metrics': {
                'total_users': total_users,
                'total_skills': total_skills,
                'total_applications': total_applications,
                'total_logs': total_logs,
            },
            'users_list': users_list,
            'recent_logs': recent_logs,
        }
        return render(request, 'core/dashboard.html', context)
        
    else:
        # --- STUDENT / STANDARD USER DASHBOARD ---
        user_skills = UserSkill.objects.filter(user=user)
        user_applications = JobApplication.objects.filter(user=user)
        
        # Skill-matching analytics calculations
        app_matches = []
        skills_set = {s.skill_name.strip().lower() for s in user_skills}
        
        for app in user_applications:
            # Parse required skills from comma-separated text
            req_skills_raw = [s.strip() for s in app.required_skills.split(',') if s.strip()]
            req_skills_lower = [s.lower() for s in req_skills_raw]
            
            matched = [s for s in req_skills_raw if s.lower() in skills_set]
            missing = [s for s in req_skills_raw if s.lower() not in skills_set]
            
            total_req = len(req_skills_lower)
            match_percentage = int((len(matched) / total_req) * 100) if total_req > 0 else 100
            
            app_matches.append({
                'application': app,
                'match_percentage': match_percentage,
                'matched_skills': matched,
                'missing_skills': missing,
                'total_required': total_req,
            })
            
        # Metrics
        total_skills_count = user_skills.count()
        total_apps_count = user_applications.count()
        pending_apps_count = user_applications.filter(status='Pending').count()
        interview_apps_count = user_applications.filter(status='Interviewing').count()
        offered_apps_count = user_applications.filter(status='Offered').count()
        
        context = {
            'is_staff': False,
            'user_skills': user_skills,
            'app_matches': app_matches,
            'metrics': {
                'total_skills': total_skills_count,
                'total_applications': total_apps_count,
                'pending': pending_apps_count,
                'interviewing': interview_apps_count,
                'offered': offered_apps_count,
            }
        }
        return render(request, 'core/dashboard.html', context)


@login_required(login_url='login')
def dashboard_metrics_view(request):
    """API Endpoint for dynamic dashboard metrics reloading"""
    user = request.user
    if user.is_staff or user.is_superuser:
        payload = {
            'metrics': {
                'total_users': User.objects.count(),
                'total_skills': UserSkill.objects.count(),
                'total_applications': JobApplication.objects.count(),
                'total_logs': AdminLog.objects.count(),
            },
            'activities': [f"{log.action_flag}: {log.change_message}" for log in AdminLog.objects.all().order_by('-action_time')[:5]]
        }
    else:
        user_skills_count = UserSkill.objects.filter(user=user).count()
        user_apps_count = JobApplication.objects.filter(user=user).count()
        offered_count = JobApplication.objects.filter(user=user, status='Offered').count()
        
        payload = {
            'metrics': {
                'total_sales': f"{user_skills_count} Skills",  # Map to existing HTML ID structure
                'active_users': f"{user_apps_count} Apps",
                'tasks': f"{offered_count} Offers",
                'notifications': 0,
            },
            'activities': [
                f"Tracked application at {app.company} as {app.job_title} ({app.status})"
                for app in JobApplication.objects.filter(user=user).order_by('-id')[:3]
            ]
        }
    return JsonResponse(payload)


# --- USER SKILLS CRUD ---

@login_required(login_url='login')
def add_skill_view(request):
    if request.method == 'POST':
        form = UserSkillForm(request.POST)
        if form.is_valid():
            skill = form.save(commit=False)
            skill.user = request.user
            skill.save()
            messages.success(request, f"Skill '{skill.skill_name}' added successfully!")
            log_action(request.user, 'ADD', f"Added skill '{skill.skill_name}' ({skill.proficiency_level})")
            return redirect('dashboard')
    else:
        form = UserSkillForm()
    return render(request, 'core/skill_form.html', {'form': form, 'title': 'Add New Skill'})


@login_required(login_url='login')
def edit_skill_view(request, skill_id):
    skill = get_object_or_404(UserSkill, id=skill_id, user=request.user)
    if request.method == 'POST':
        form = UserSkillForm(request.POST, instance=skill)
        if form.is_valid():
            form.save()
            messages.success(request, f"Skill '{skill.skill_name}' updated successfully!")
            log_action(request.user, 'EDIT', f"Updated skill '{skill.skill_name}' to {skill.proficiency_level}")
            return redirect('dashboard')
    else:
        form = UserSkillForm(instance=skill)
    return render(request, 'core/skill_form.html', {'form': form, 'title': f"Edit Skill: {skill.skill_name}"})


@login_required(login_url='login')
def delete_skill_view(request, skill_id):
    skill = get_object_or_404(UserSkill, id=skill_id, user=request.user)
    skill_name = skill.skill_name
    skill.delete()
    messages.success(request, f"Skill '{skill_name}' deleted successfully.")
    log_action(request.user, 'DEL', f"Deleted skill '{skill_name}'")
    return redirect('dashboard')


# --- JOB APPLICATIONS CRUD ---

@login_required(login_url='login')
def add_job_view(request):
    if request.method == 'POST':
        form = JobApplicationForm(request.POST)
        if form.is_valid():
            job = form.save(commit=False)
            job.user = request.user
            job.save()
            messages.success(request, f"Job tracking at '{job.company}' added!")
            log_action(request.user, 'ADD', f"Added job application: {job.job_title} at {job.company}")
            return redirect('dashboard')
    else:
        form = JobApplicationForm()
    return render(request, 'core/job_form.html', {'form': form, 'title': 'Track New Job Application'})


@login_required(login_url='login')
def edit_job_view(request, job_id):
    job = get_object_or_404(JobApplication, id=job_id, user=request.user)
    if request.method == 'POST':
        form = JobApplicationForm(request.POST, instance=job)
        if form.is_valid():
            form.save()
            messages.success(request, f"Application details for '{job.company}' updated!")
            log_action(request.user, 'EDIT', f"Updated job application: {job.job_title} at {job.company} status to {job.status}")
            return redirect('dashboard')
    else:
        form = JobApplicationForm(instance=job)
    return render(request, 'core/job_form.html', {'form': form, 'title': f"Edit Application: {job.job_title} at {job.company}"})


@login_required(login_url='login')
def delete_job_view(request, job_id):
    job = get_object_or_404(JobApplication, id=job_id, user=request.user)
    company = job.company
    job_title = job.job_title
    job.delete()
    messages.success(request, f"Job application for '{job_title}' at '{company}' deleted.")
    log_action(request.user, 'DEL', f"Deleted job application: {job_title} at {company}")
    return redirect('dashboard')


# --- ADMIN SPECIFIC VIEWS ---

@login_required(login_url='login')
@user_passes_test(lambda u: u.is_staff or u.is_superuser, login_url='login')
def toggle_staff_view(request, user_id):
    target_user = get_object_or_404(User, id=user_id)
    if target_user == request.user:
        messages.error(request, "You cannot modify your own staff privileges.")
        return redirect('dashboard')
        
    target_user.is_staff = not target_user.is_staff
    target_user.save()
    status_str = "granted" if target_user.is_staff else "revoked"
    messages.success(request, f"Staff privileges for '{target_user.username}' successfully {status_str}.")
    log_action(request.user, 'EDIT', f"Toggled staff status for user '{target_user.username}' (New Status: {target_user.is_staff})")
    return redirect('dashboard')


@login_required(login_url='login')
@user_passes_test(lambda u: u.is_staff or u.is_superuser, login_url='login')
def admin_logs_view(request):
    logs = AdminLog.objects.all().order_by('-action_time')
    return render(request, 'core/admin_logs.html', {'logs': logs})
