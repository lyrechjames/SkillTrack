from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from .models import UserSkill, JobApplication

User = get_user_model()

# 1. Registration Form
class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(required=True, help_text="Required. A valid email address.")
    first_name = forms.CharField(max_length=30, required=True, help_text="Required.")
    last_name = forms.CharField(max_length=30, required=True, help_text="Required.")

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("A user with this email address already exists.")
        return email

# 2. User Profile Form
class UserProfileForm(forms.ModelForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']

# 3. User Skill Form
class UserSkillForm(forms.ModelForm):
    PROFICIENCY_CHOICES = [
        ('Beginner', 'Beginner'),
        ('Intermediate', 'Intermediate'),
        ('Advanced', 'Advanced'),
        ('Expert', 'Expert'),
    ]
    proficiency_level = forms.ChoiceField(choices=PROFICIENCY_CHOICES, widget=forms.Select(attrs={'class': 'form-select'}))
    
    class Meta:
        model = UserSkill
        fields = ['skill_name', 'proficiency_level', 'category']
        widgets = {
            'skill_name': forms.TextInput(attrs={'placeholder': 'e.g., Python, Docker, AWS', 'class': 'form-control'}),
            'category': forms.TextInput(attrs={'placeholder': 'e.g., Backend, DevOps, Frontend', 'class': 'form-control'}),
        }

# 4. Job Application Form
class JobApplicationForm(forms.ModelForm):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Interviewing', 'Interviewing'),
        ('Offered', 'Offered'),
        ('Rejected', 'Rejected'),
    ]
    status = forms.ChoiceField(choices=STATUS_CHOICES, initial='Pending', widget=forms.Select(attrs={'class': 'form-select'}))

    class Meta:
        model = JobApplication
        fields = ['company', 'job_title', 'status', 'required_skills']
        widgets = {
            'company': forms.TextInput(attrs={'placeholder': 'e.g., Google, Stripe', 'class': 'form-control'}),
            'job_title': forms.TextInput(attrs={'placeholder': 'e.g., Software Engineer, DevOps Analyst', 'class': 'form-control'}),
            'required_skills': forms.Textarea(attrs={'placeholder': 'e.g., Python, SQL, AWS (comma-separated)', 'rows': 3, 'class': 'form-control'}),
        }
