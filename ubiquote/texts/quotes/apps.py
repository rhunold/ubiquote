from django.apps import AppConfig


class QuotesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'texts.quotes'
    label = 'quotes'    
    
    # def ready(self):
    #     import texts.translation  # ceci est safe ici        
