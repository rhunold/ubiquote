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
    fullname = models.CharField(max_length=255, blank=True, null=True)
    # ordering = models.CharField(max_length=255, blank=True, null=True)  # New field for manual ordering

    # biography = models.TextField(max_length=500, blank=True, verbose_name="Biography :")
    # user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, blank=True)
    # signature = models.ImageField(_('signature'),upload_to='signature/authors/', null=True, blank=True, default='signature/default.png')       
    
    avatar = models.ImageField(_('avatar'),upload_to='avatars/authors/', null=True, blank=True, default='avatars/default.png')
 
    
    slug = AutoSlugField(populate_from='generate_slug', unique=True, null=True, default=None)
  
    
    def generate_slug(self):
        # Customize this method to generate the slug from the desired field(s)
        if self.nickname:
            return self.nickname
        elif self.title:
            return f'{self.title}  {self.last_name}'       
        else:
            return f'{self.first_name or ""} {self.middle_name or ""} {self.particul or ""}  {self.last_name or ""}'
        
    
    
    # def upload_avatar(instance, filename):
    #     return f'avatars/authors/{instance.generate_slug()}_{filename}'    
    
    def __str__(self):
        # if self.nickname:
        #     return self.nickname
        # else:
        #     return f' {self.title or ""} {self.first_name or ""} {self.middle_name or ""} {self.particul or ""} {self.last_name or ""}'        
        
        return f'{self.fullname or ""}'
    
    def generate_fullname(self):
        # order = self.ordering.split(',') if self.ordering else None
        components = [ self.last_name ,self.nickname, self.first_name, self.middle_name]

        # if order:
        #     # Sort the components based on the specified order
        #     components.sort(key=lambda x: order.index(x) if x in order else len(order))
            


        non_empty_components = [component for component in components if component]

        if non_empty_components:
            # print(" ".join(non_empty_components))
            return " ".join(non_empty_components)
        else:
            return None
            
    
    def save(self, *args, **kwargs):
        self.fullname = self.generate_fullname()
        # self.slug = self.generate_slug()        
        # print(f"Saving author with fullname: {self.fullname}")
        super().save(*args, **kwargs)       
        

    def count_authors():
        count = Author.objects.count()
        return count
    
    class Meta:
       ordering = ['fullname']
       
# # Save all instance to generate the new fullname
# for author in Author.objects.all():
#     author.save()
 
 

class AuthorAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        # Don't forget to filter out results depending on the visitor !
        if not self.request.user.is_authenticated:
            return Author.objects.none()

        qs = Author.objects.all().order_by('last_name')

        # if self.q:
            # qs = qs.filter(last_name__istartswith=self.q)

        if self.q:
            qs = qs.filter(
                Q(fullname__icontains=self.q) 
                # Q(particul__icontains=self.q) |
                # Q(last_name__icontains=self.q) |
                # Q(first_name__istartswith=self.q) |
                # Q(middle_name__istartswith=self.q) |
                # Q(nickname__istartswith=self.q)
                )
        return qs
    
    def get_result_label(self, result):
        # return result
        return format_html('{}', result)