# SkillTrack

SkillTrack is a centralized, web-based software platform designed to help students systematically organize, store, and manage their professional certifications and technical skills. The system bridges the gap between individual student portfolios and institutional evaluation by providing role-specific access to students, faculty advisers, and academic coordinators. Ultimately, it optimizes how credentials are tracked, searched, and verified throughout a student's academic journey.

## Objectives

- To establish a secure digital repository for storing and managing diverse certification records.
- To accurately monitor and track student technical proficiency and training achievements over time.
- To enable rapid, granular retrieval of specific records using an advanced multi-attribute search engine.
- To generate comprehensive, exportable performance and accomplishment reports for academic or professional evaluation.

## Features

- User authentication with login, registration, and password recovery flows.
- Protected dashboard access for authenticated users.
- Centralized management of academic and professional credential records.

## Getting Started

1. Create and activate a virtual environment.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Apply migrations:
   ```bash
   python manage.py migrate
   ```
4. Run the development server:
   ```bash
   python manage.py runserver
   ```

## Project Structure

- `config/` — Django project settings and URL configuration.
- `core/` — Authentication views, templates, and core app logic.
- `db.sqlite3` — Local development database.

