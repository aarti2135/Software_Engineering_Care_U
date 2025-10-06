# usermanagement/apps.py
from django.apps import AppConfig

class UsermanagementConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "usermanagement"

    def ready(self):
        # Import signals so they register with Django
        from . import signals  # noqa: F401
