from django.db import models
from django.contrib.auth.models import AbstractUser

# 1. Custom User Model (Handles is_staff, is_superuser automatically)
class User(AbstractUser):
    email = models.EmailField(unique=True)
    
    def __str__(self):
        return self.username

# 2. User Skills Model
class UserSkill(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="skills")
    skill_name = models.CharField(max_length=100)
    proficiency_level = models.CharField(max_length=50) # e.g., Beginner, Intermediate, Expert
    category = models.CharField(max_length=100)        # e.g., Backend, Frontend, Cloud

    def __str__(self):
        return f"{self.user.username} - {self.skill_name}"

# 3. Job Application Model
class JobApplication(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="applications")
    company = models.CharField(max_length=150)
    job_title = models.CharField(max_length=150)
    status = models.CharField(max_length=50, default="Pending") # e.g., Pending, Interviewing, Offered, Rejected
    application_date = models.DateTimeField(auto_now_add=True)
    required_skills = models.TextField() # Comma-separated list of required skills

    def __str__(self):
        return f"{self.job_title} at {self.company}"

# 4. Admin Log Model
class AdminLog(models.Model):
    ACTION_CHOICES = [
        ('ADD', 'ADD'),
        ('EDIT', 'EDIT'),
        ('DEL', 'DEL'),
    ]
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    action_time = models.DateTimeField(auto_now_add=True)
    action_flag = models.CharField(max_length=4, choices=ACTION_CHOICES)
    change_message = models.TextField()

    def __str__(self):
        return f"{self.action_flag} by {self.user.username if self.user else 'Unknown'}"
