from django.db import models

# from django.core.exceptions import ValidationError
# import os

from .constants import SEX_CHOICES, NATIONALITIES_CHOICES

from django.conf import settings
LANGUAGES = settings.LANGUAGES



# from django.urls import reverse


class Person(models.Model):
    first_name = models.CharField(max_length=30, null=True, blank=True)
    middle_name = models.CharField(max_length=30, null=True, blank=True)
    last_name = models.CharField(max_length=30, null=True, blank=True)

    date_birth = models.DateField('birthday', null=True, blank=True)
    date_death = models.DateField('death', null=True, blank=True)
    
    sex = models.CharField(max_length=1,choices=SEX_CHOICES, null=True, blank=True)
    nationality = models.CharField(choices=NATIONALITIES_CHOICES, null=True, blank=True)

    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    
    
    biography = models.TextField(max_length=500, blank=True, verbose_name="Biography :")    

    twitter_url = models.URLField(max_length=200, null=True, blank=True, default='http://www.twitter.com/')


    class Meta:
        abstract = True
