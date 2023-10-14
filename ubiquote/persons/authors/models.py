from django.db import models
from ..models import Person
from persons.users.models import User
from autoslug import AutoSlugField

class Author(Person):
    nickname = models.CharField(max_length=30, null=True, blank=True)
    # biography = models.TextField(max_length=500, blank=True, verbose_name="Biography :")
    user = models.OneToOneField(User,  on_delete=models.SET_NULL, null=True, blank=True)
    
    avatar = models.ImageField(upload_to='avatars/authors/', null=True, blank=True, default='avatars/default.png')
    
    slug = AutoSlugField(populate_from='generate_slug', unique=True, null=True, default=None)
  
    
    def generate_slug(self):
        # Customize this method to generate the slug from the desired field(s)
        if self.nickname:
            return self.nickname
        else:
            return f'{self.first_name or ""} {self.middle_name or ""} {self.last_name or ""}'
    
    
    # def upload_avatar(instance, filename):
    #     return f'avatars/authors/{instance.generate_slug()}_{filename}'    
    
    def __str__(self):
        if self.nickname is not None:
            return f'{self.nickname}'
        else:
            return f'{self.first_name or ""} {self.middle_name or ""} {self.last_name or ""}'
        

    def count_authors():
        count = Author.objects.count()
        return count        
        
    