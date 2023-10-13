from django.db import models
from autoslug import AutoSlugField

from django.contrib.auth.models import AbstractUser
# from .overrides import UserManager

from ..models import Person


class User(AbstractUser, Person):
    username = models.CharField(max_length=30)
    email = models.EmailField(verbose_name='email address', max_length=255, unique=True)
    # client = models.BooleanField(default=False, blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username',]

    slug = AutoSlugField(populate_from='username', unique=True, null=True, default=None)
    
    
    avatar = models.ImageField(upload_to='avatars/users/', null=True, blank=True, default='avatars/default.png')    
        
    # objects = UserManager()
    
    def __str__(self):
        return f'{self.username}'
    
    # class Meta:
    #     app_label = "user"    
