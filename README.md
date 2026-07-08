# SkillTrack

SkillTrack is a centralized, web-based software platform designed to help students systematically organize, store, and manage their professional certifications, technical skills, and job applications. The system bridges the gap between individual student portfolios and institutional evaluation by providing role-specific dashboards for standard users and staff members.

## Features

- **User Authentication**: Secure registration, login, logout, and lockout security mechanisms.
- **Skill Tracking**: Manage personal technical skills, categorized by technology area and proficiency level.
- **Job Application Tracking**: Track applications sent to companies, statuses (Pending, Interviewing, Offered, Rejected), dates, and required skills.
- **Skill Matching Analysis**: Interactive dashboard comparing your skills list to a job's required skills, giving a percentage match and checklist of missing skills!
- **Administrative Logging**: Activity logging (`AdminLog`) tracking modifications for audit trails.
- **Role-Based Dashboards**:
  - *Standard Users*: Visualization of skill stats, job funnel metrics, and interactive skill matching.
  - *Staff/Admin Users*: Global analytics, user account status manager, and system admin logs.

## Technology Stack

- **Backend**: Django (Python)
- **Database**: SQLite
- **Frontend**: HTML5, Vanilla CSS3, Javascript (ES6+)

## Getting Started

1. Clone the repository:
   ```bash
   git clone https://github.com/jameslyrech-byte/SkillTrack.git
   cd SkillTrack
   ```
2. Set up virtual environment:
   ```bash
   python -m venv .venv
   .venv\Scripts\activate  # Windows
   source .venv/bin/activate  # macOS/Linux
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Run migrations:
   ```bash
   python manage.py makemigrations core
   python manage.py migrate
   ```
5. Create staff superuser:
   ```bash
   python manage.py createsuperuser
   ```
6. Run the server:
   ```bash
   python manage.py runserver
   ```
