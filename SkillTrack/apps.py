from django.apps import AppConfig


class SkillTrackConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'SkillTrack'
    # The production Supabase schema was originally migrated under this app
    # label (core_user, core_userskill, etc.). Keep the label stable so the
    # application uses those existing tables instead of looking for new
    # SkillTrack_* tables.
    label = 'core'
