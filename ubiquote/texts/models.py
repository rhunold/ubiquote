from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from persons.users.models import User
# from texts.quotes.models import Quote

import os

from django.conf import settings
# LANGUAGES = settings.LANGUAGES

from django.db.models.functions import Substr


from django.urls import reverse
from autoslug import AutoSlugField
from django.utils.text import slugify

     

def default_contributor():
    admin_email = os.environ.get('ADMIN_EMAIL')
    if not admin_email:
        
        # For test/debugging
        raise ImproperlyConfigured("ADMIN_EMAIL must be set in environment variables.")        
    
        # for prod
        # logger.warning("ADMIN_EMAIL is not set in environment variables.")
        # return None

    try:
        return User.objects.get(email=admin_email).id
    except User.DoesNotExist:
        # For test/debugging        
        raise ImproperlyConfigured(f"No user found with ADMIN_EMAIL: {admin_email}")
    
        # for prod
        # logger.warning(f"No user found with ADMIN_EMAIL: {admin_email}")
        # return None    
    
    
    
    # admin_email = os.environ.get('ADMIN_EMAIL')
    # try:
    #     return User.objects.get(email=admin_email).id
    # except User.DoesNotExist:
    #     # Gérer le cas où l'utilisateur n'existe pas
    #     return None
    

class Text(models.Model):
    
    class PublishedManager(models.Manager):
        def get_queryset(self):
            return super().get_queryset() .filter(status='published')
        
    status_options = (
        ('unpublished', _('unpublished')),
        ('published', _('published'))
    )
    
    # Define the default manager
    objects = models.Manager()   
    
    
    status = models.CharField(_('status'),max_length=20, choices=status_options, default='published')
    # objects = models.Manager() # Defaut Manager
    published = PublishedManager() # to make query preformated : Post.published.all() vs Post.objects.all()     

    text = models.TextField(_('Text'), max_length=1000) # max_length=500, default="Default value",  verbose_name="Text Content :"
    lang = models.CharField(_('Langs'), max_length=2, choices=settings.LANGUAGES, default="en")
    
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
        
    slug = models.SlugField(unique=True, blank=True, null=True, max_length=200)  # Remove AutoSlugField

    def generate_slug(self):
        base_slug = slugify(self.text[:100]) or "text"
        return f"{base_slug}-{self.id}"

    def save(self, *args, **kwargs):
        # if not self.date_created:
        #     self.date_created = now()        
        
        
        super().save(*args, **kwargs)  # First save to get the ID
        if not self.slug or self.slug.endswith('-none'):
            self.slug = self.generate_slug()
            super().save(update_fields=["slug"])   

    

    contributor = models.ForeignKey(
        User,
        related_name="%(app_label)s_%(class)s_related",
        related_query_name="%(app_label)s_%(class)ss",

        on_delete=models.SET_DEFAULT,
        # default=None
        default=default_contributor,
        null=True
        
        )


    
    

    class Meta:
        abstract = True
        ordering = ['date_created']
        
        
    


class Category(models.Model):
    title = models.CharField(max_length=100, verbose_name="Category Title :")
    # add snippet ?
    text = models.TextField(verbose_name=" Text :")
    slug = AutoSlugField(populate_from='title', unique=True, null=True, default=None)
    
    def __str__(self):
        return f'{self.title}'

    def count_categories():
        count = Category.objects.count()
        return count      
    
    # def get_translated_title(self, lang_code):
    #     translation = self.translations.filter(lang=lang_code).first()
    #     return translation.title if translation else self.title
     
    

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)  
        
          
    class Meta:
        verbose_name_plural = "Categories"     
        # ordering = ['title']        
        

# # Save all instance to generate the new slug
# for obj in Category.objects.all():
#     obj.save()


