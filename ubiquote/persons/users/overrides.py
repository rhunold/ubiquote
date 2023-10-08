# from rest_framework.permissions import DjangoModelPermissions
# from rest_framework.views import exception_handler

from django.contrib.auth.base_user import BaseUserManager


# def custom_exception_handler(exc, context):
#     # Call REST framework's default exception handler first,
#     # to get the standard error response.
#     response = exception_handler(exc, context)
        
#     if response is not None:
#         response.data['status_code'] = response.status_code

#     return response



class UserManager(BaseUserManager):
    """Overide the Manager to allow superuser to be create with an email and not a username"""    
    
    use_in_migrations = True

    def _create_user(self, username, email, password, **extra_fields):
        if not email:
            raise ValueError('Users require an email field')
        if not username:
            raise ValueError('Users require an username field')        
        email = self.normalize_email(email)
        # username = self.normalize_username(username)        
        user = self.model(username=username,email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, username, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(usernamen, email, password, **extra_fields)

    def create_superuser(self, username, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(username, email, password, **extra_fields)


# class AddGetDjangoModelPermissions(DjangoModelPermissions):
#     def __init__(self):
#         self.perms_map['GET'] = ['%(app_label)s.view_%(model_name)s']
        
