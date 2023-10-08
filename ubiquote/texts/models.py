from django.db import models
from django.core.exceptions import ValidationError

from persons.users.models import User

import os

from django.conf import settings
LANGUAGES = settings.LANGUAGES

from django.urls import reverse
from autoslug import AutoSlugField
     

def default_contributor():
    admin_email = os.environ.get('ADMIN_EMAIL')
    return User.objects.get(email=admin_email)
    

class Text(models.Model):
    text = models.TextField(max_length=500, verbose_name="Text Content :") #, default="Default value"
    lang = models.CharField(max_length=2, choices=LANGUAGES, default="fr")

    contributor = models.ForeignKey(
        User,
        related_name="%(app_label)s_%(class)s_related",
        related_query_name="%(app_label)s_%(class)ss",
        null=True,
        on_delete=models.SET_DEFAULT,
        default=None
        # default=default_contributor
        )

    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    

    class Meta:
        abstract = True
        ordering = ['date_created']


class Category(models.Model):
    title = models.CharField(max_length=100, verbose_name="Category Title :")
    text = models.TextField(max_length=500, verbose_name=" Text :")
    slug = AutoSlugField(populate_from='title', unique=True, null=True, default=None)
    
    def __str__(self):
        return f'{self.title}'
    
    class Meta:
        verbose_name_plural = "Categories"     
