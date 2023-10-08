from django.db import models
from ..models import Person
from autoslug import AutoSlugField

class Author(Person):
    nickname = models.CharField(max_length=30, null=True, blank=True)
    biography = models.TextField(max_length=500, blank=True, verbose_name="Biography :")
    slug = AutoSlugField(populate_from='generate_slug', unique=True, null=True, default=None)    
    
    def generate_slug(self):
        # Customize this method to generate the slug from the desired field(s)
        if self.nickname:
            return self.nickname
        else:
            return f'{self.first_name or ""} {self.middle_name or ""} {self.last_name or ""}'
    
    
    def __str__(self):
        if self.nickname is not None:
            return f'{self.nickname}'
        else:
            return f'{self.first_name or ""} {self.middle_name or ""} {self.last_name or ""}'
        
    