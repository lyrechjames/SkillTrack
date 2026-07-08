from django.contrib.auth import views as auth_views
from django.shortcuts import redirect
from django.urls import path

from . import views

urlpatterns = [
    path('', lambda request: redirect('login')),
    path('login/', views.login_view, name='login'),
    path('login-alt/', views.login_view_alt, name='login_alt'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path(
        'password-reset/',
        auth_views.PasswordResetView.as_view(template_name='core/password_reset.html'),
        name='password_reset',
    ),
    path(
        'password-reset/done/',
        auth_views.PasswordResetDoneView.as_view(template_name='core/password_reset_done.html'),
        name='password_reset_done',
    ),
    path(
        'password-reset-confirm/<uidb64>/<token>/',
        auth_views.PasswordResetConfirmView.as_view(template_name='core/password_reset_confirm.html'),
        name='password_reset_confirm',
    ),
    path(
        'password-reset-complete/',
        auth_views.PasswordResetCompleteView.as_view(template_name='core/password_reset_complete.html'),
        name='password_reset_complete',
    ),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('dashboard/metrics/', views.dashboard_metrics_view, name='dashboard_metrics'),
    path('skills/add/', views.add_skill_view, name='add_skill'),
    path('skills/<int:skill_id>/edit/', views.edit_skill_view, name='edit_skill'),
    path('skills/<int:skill_id>/delete/', views.delete_skill_view, name='delete_skill'),
    path('jobs/add/', views.add_job_view, name='add_job'),
    path('jobs/<int:job_id>/edit/', views.edit_job_view, name='edit_job'),
    path('jobs/<int:job_id>/delete/', views.delete_job_view, name='delete_job'),
    path('users/<int:user_id>/toggle-staff/', views.toggle_staff_view, name='toggle_staff'),
    path('admin-logs/', views.admin_logs_view, name='admin_logs'),
]
