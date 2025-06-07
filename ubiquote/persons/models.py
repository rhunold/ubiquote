from django.db import models

# from django.core.exceptions import ValidationError
# import os
from django.core.exceptions import ValidationError
from datetime import datetime



from .constants import SEX_CHOICES, NATIONALITIES_CHOICES

from django.utils.translation import gettext_lazy as _

# from django.conf import settings
# LANGUAGES = settings.LANGUAGES

from flexidate import parse

from django.core.validators import RegexValidator


class Person(models.Model):
    first_name = models.CharField(_('first name'), max_length=30, null=True, blank=True)
    middle_name = models.CharField(_('middle name'), max_length=30, null=True, blank=True)
    last_name = models.CharField(_('last name'), max_length=50, null=True, blank=True)
    particul = models.CharField(_('particul'), max_length=5, null=True, blank=True)
    title = models.CharField(_('title'), max_length=15, null=True, blank=True)
    

    date_birth_datefield = models.DateField(_('birthday_datefield'), null=True, blank=True)
    
    date_birth = models.CharField(_('birthday'), 
                                  max_length=30, null=True, blank=True,
                                  validators=[
                                        RegexValidator(
                                            regex=r'^-?\d{4}-(0[1-9]|1[0-2])-(0[1-9]|[1-2][0-9]|3[0-1])$',
                                            message=_(
                                                "Enter a valid date in the format 'YYYY-MM-DD' or '-YYYY-MM-DD'. "
                                                "Year must be numeric. Month must be 01 to 12. Day must be 01 to 31."
                                            ),
                                        )
                                    ],
                                    help_text = "Format is YYYY-MM-DD or -YYYY-MM-DD",
                                  
                                  ) # in the view date_birth = FlexiDate(Author.date_birth)   
      
    date_death_datefield = models.DateField(_('death_datefield'), null=True, blank=True)
    
    date_death = models.CharField(_('death'), 
                                  max_length=30, null=True, blank=True,
                                  validators=[
                                        RegexValidator(
                                            regex=r'^-?\d{4}-(0[1-9]|1[0-2])-(0[1-9]|[1-2][0-9]|3[0-1])$',
                                            message=_(
                                                "Enter a valid date in the format 'YYYY-MM-DD' or '-YYYY-MM-DD'. "
                                                "Year must be numeric. Month must be 01 to 12. Day must be 01 to 31."
                                            ),
                                        )
                                    ],
                                    help_text = "Format is YYYY-MM-DD or -YYYY-MM-DD",                                  
                                  )    
    
    sex = models.CharField(_('sex'), max_length=1,choices=SEX_CHOICES, null=True, blank=True)
    nationality = models.CharField(_('nationality'), choices=NATIONALITIES_CHOICES, null=True, blank=True)

    date_created = models.DateTimeField(_('date created'), auto_now_add=True)
    date_updated = models.DateTimeField(_('date updated'), auto_now=True)
    
    
    biography = models.TextField(_('biography'), max_length=500, blank=True)    

    twitter_url = models.URLField(max_length=200, null=True, blank=True, default='http://www.twitter.com/')
        
        
            
    def clean(self):
            # Validate and set birth date
            if self.date_birth:
                if self.date_birth.startswith('-'):
                    self.date_birth_datefield = None
                else:
                    try:
                        self.date_birth_datefield = datetime.strptime(self.date_birth, '%Y-%m-%d').date()
                    except ValueError:
                        self.date_birth_datefield = None
            else:
                self.date_birth_datefield = None

            # Validate and set death date
            if self.date_death:
                if self.date_death.startswith('-'):
                    self.date_death_datefield = None
                else:
                    try:
                        self.date_death_datefield = datetime.strptime(self.date_death, '%Y-%m-%d').date()
                    except ValueError:
                        self.date_death_datefield = None
            else:
                self.date_death_datefield = None
    
    # def save(self, *args, **kwargs):
    #     self.date_birth_datefield, self.date_birth = self._normalize_dates(self.date_birth)
    #     self.date_death_datefield, self.date_death = self._normalize_dates(self.date_death)    
    #     super().save(*args, **kwargs)

    # def _normalize_dates(self, raw_date):
    #     """
    #     Returns a tuple: (datefield_value, charfield_value)
    #     Only one will be non-None:
    #       - AD valid → (datetime.date, None)
    #       - BCE or invalid → (None, original string)
    #     """
    #     if raw_date:
    #         try:
    #             sign = -1 if raw_date.startswith('-') else 1
    #             parts = raw_date.lstrip('-').split('-')
    #             year, month, day = map(int, parts)
    #             if sign == 1 and year >= 1:
    #                 return datetime.date(year, month, day), None
    #         except Exception:
    #             pass
    #         return None, raw_date
    #     return None, None    
    
    # def update_date_field(self, field_value, datefield):
    #     if field_value:
    #         try:
    #             parsed_date = parse(field_value)
    #             date_as_datetime = parsed_date.as_datetime()
    #             setattr(self, datefield, date_as_datetime)
    #         except Exception as e:
    #             print(f"Error parsing date: {e}")
    #             setattr(self, datefield, None)
    #     else:
    #         setattr(self, datefield, None)

    # def update_date_birth_datefield(self):
    #     self.update_date_field(self.date_birth, 'date_birth_datefield')

    # def update_date_death_datefield(self):
    #     self.update_date_field(self.date_death, 'date_death_datefield')


    # def save(self, *args, **kwargs):
    #     print(f"save from Text {type(self.date_birth_datefield)}")
    #     self.update_date_birth_datefield()
    #     self.update_date_death_datefield()
    #     super().save(*args, **kwargs)    

    class Meta:
        abstract = True
