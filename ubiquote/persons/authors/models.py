from django.db import models
from ..models import Person
from persons.users.models import User
from autoslug import AutoSlugField
from django.utils.translation import gettext_lazy as _

from dal import autocomplete
from django.utils.html import format_html
from django.db.models import Q

# import autocomplete_light

class Author(Person):
    nickname = models.CharField(_('nickname'), max_length=30, null=True, blank=True)
    # biography = models.TextField(max_length=500, blank=True, verbose_name="Biography :")
    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, blank=True)
    
    avatar = models.ImageField(_('avatar'),upload_to='avatars/authors/', null=True, blank=True, default='avatars/default.png')
    
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
        return f'{self.nickname or ""} {self.first_name or ""} {self.middle_name or ""} {self.last_name or ""}'
        

    def count_authors():
        count = Author.objects.count()
        return count        
        
        
        
 

class AuthorAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        # Don't forget to filter out results depending on the visitor !
        if not self.request.user.is_authenticated:
            return Author.objects.none()

        qs = Author.objects.all()

        if self.q:
            # qs = qs.filter(last_name__istartswith=self.q)
            
            qs = qs.filter(Q(last_name__istartswith=self.q) | Q(nickname__istartswith=self.q))
            

        return qs
    
    def get_result_label(self, result):
        # return result
        return format_html('{}', result)