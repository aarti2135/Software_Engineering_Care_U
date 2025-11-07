from django.apps import AppConfig

class ProactiveFeatConfig(AppConfig):
    name = "proactive_feat"
    verbose_name = "Proactive Health Features"

    def ready(self):
        from . import signals  # register signal handlers
