from django.apps import AppConfig


class UsersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'persons.users'
    label = 'users'    

    # def ready(self):
    #     from persons.users import User