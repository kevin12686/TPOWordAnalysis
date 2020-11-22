from django.apps import AppConfig


class WordfrequencyConfig(AppConfig):
    name = 'WordFrequency'

    def ready(self):
        from .signals import parse_word
