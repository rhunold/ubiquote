from django.db import models

# from django.core.exceptions import ValidationError
# import os



from .constants import SEX_CHOICES, NATIONALITIES_CHOICES

from django.utils.translation import gettext_lazy as _

from django.conf import settings
LANGUAGES = settings.LANGUAGES

from flexidate import parse


class Person(models.Model):
    first_name = models.CharField(_('first name'), max_length=30, null=True, blank=True)
    middle_name = models.CharField(_('middle name'), max_length=30, null=True, blank=True)
    last_name = models.CharField(_('last name'), max_length=50, null=True, blank=True)
    particul = models.CharField(_('particul'), max_length=5, null=True, blank=True)
    title = models.CharField(_('title'), max_length=15, null=True, blank=True)
    

    date_birth_datefield = models.DateField(_('birthday_datefield'), null=True, blank=True)
    date_birth = models.CharField(_('birthday'), max_length=30, null=True, blank=True) # in the view date_birth = FlexiDate(Author.date_birth)   
      
    date_death_datefield = models.DateField(_('death_datefield'), null=True, blank=True)
    date_death = models.CharField(_('death'), max_length=30, null=True, blank=True)    
    
    sex = models.CharField(_('sex'), max_length=1,choices=SEX_CHOICES, null=True, blank=True)
    nationality = models.CharField(_('nationality'), choices=NATIONALITIES_CHOICES, null=True, blank=True)

    date_created = models.DateTimeField(_('date created'), auto_now_add=True)
    date_updated = models.DateTimeField(_('date updated'), auto_now=True)
    
    
    biography = models.TextField(_('biography'), max_length=500, blank=True)    

    twitter_url = models.URLField(max_length=200, null=True, blank=True, default='http://www.twitter.com/')
    
    def update_date_field(self, field_value, datefield):
        if field_value:
            try:
                parsed_date = parse(field_value)
                date_as_datetime = parsed_date.as_datetime()
                setattr(self, datefield, date_as_datetime)
            except Exception as e:
                print(f"Error parsing date: {e}")
                setattr(self, datefield, None)
        else:
            setattr(self, datefield, None)

    def update_date_birth_datefield(self):
        self.update_date_field(self.date_birth, 'date_birth_datefield')

    def update_date_death_datefield(self):
        self.update_date_field(self.date_death, 'date_death_datefield')


    def save(self, *args, **kwargs):
        self.update_date_birth_datefield()
        self.update_date_death_datefield()
        super().save(*args, **kwargs)    

    class Meta:
        abstract = True
