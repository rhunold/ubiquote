from django.db import models

# from django.core.exceptions import ValidationError
# import os

from .constants import SEX_CHOICES, NATIONALITIES_CHOICES

from django.utils.translation import gettext_lazy as _

from django.conf import settings
LANGUAGES = settings.LANGUAGES



# from django.urls import reverse


class Person(models.Model):
    first_name = models.CharField(_('first name'), max_length=30, null=True, blank=True)
    middle_name = models.CharField(_('middle name'), max_length=30, null=True, blank=True)
    last_name = models.CharField(_('last name'), max_length=50, null=True, blank=True)

    date_birth = models.DateField(_('birthday'), null=True, blank=True)
    date_death = models.DateField(_('death'), null=True, blank=True)
    
    sex = models.CharField(_('sex'), max_length=1,choices=SEX_CHOICES, null=True, blank=True)
    nationality = models.CharField(_('nationality'), choices=NATIONALITIES_CHOICES, null=True, blank=True)

    date_created = models.DateTimeField(_('date created'), auto_now_add=True)
    date_updated = models.DateTimeField(_('date updated'), auto_now=True)
    
    
    biography = models.TextField(_('biography'), max_length=500, blank=True)    

    twitter_url = models.URLField(max_length=200, null=True, blank=True, default='http://www.twitter.com/')


    class Meta:
        abstract = True
