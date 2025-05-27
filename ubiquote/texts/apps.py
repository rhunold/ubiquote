from django.apps import AppConfig


class TextsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'texts'
    

    # def ready(self):
    #     import texts.translation  # ceci est safe ici    
