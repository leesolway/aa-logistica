from django.apps import AppConfig


class LogisticaConfig(AppConfig):
    name = "logistica"
    verbose_name = "Logistica"

    def ready(self):
        try:
            from . import auth_hooks  # noqa: F401
        except Exception:
            pass
