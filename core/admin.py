from django.contrib import admin

from .models import UserSkill, JobApplication, AdminLog


@admin.register(UserSkill)
class UserSkillAdmin(admin.ModelAdmin):
    list_display = ['user', 'skill_name', 'proficiency_level', 'category']
    list_filter = ['proficiency_level', 'category']
    search_fields = ['user__username', 'skill_name']


@admin.register(JobApplication)
class JobApplicationAdmin(admin.ModelAdmin):
    list_display = ['user', 'company', 'job_title', 'status', 'application_date']
    list_filter = ['status', 'application_date']
    search_fields = ['company', 'job_title', 'user__username']


@admin.register(AdminLog)
class AdminLogAdmin(admin.ModelAdmin):
    list_display = ['user', 'action_flag', 'action_time', 'change_message']
    list_filter = ['action_flag', 'action_time']
    search_fields = ['user__username', 'action_flag', 'change_message']
