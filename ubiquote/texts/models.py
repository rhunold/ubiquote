from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from persons.users.models import User
# from texts.quotes.models import Quote

import os

from django.conf import settings
LANGUAGES = settings.LANGUAGES

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
        ('draft', _('draft')),
        ('published', _('published'))
    )
    
    # Define the default manager
    objects = models.Manager()    
    
    
    # text_input = models.TextField(_('Text'), max_length=1000)
    # text_cleaned = models.TextField(_('Text cleaned'), max_length=1000)    # vide au debut=> ajouter methode pour le generer (detetection de lang puis formatage...)
    
    text = models.TextField(_('Text'), max_length=1000) # max_length=500, default="Default value",  verbose_name="Text Content :"
    lang = models.CharField(_('Langs'), max_length=2, choices=LANGUAGES, default="fr")
    
    
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
        
        
    # snippet = models.CharField(max_length=100, editable=False)
    
    # slug = models.SlugField(unique=True, blank=True, null=True, default=None)

    # def generate_unique_slug(self):
    #     # Use text content to create base slug
    #     base_slug = slugify(self.text[:100]) or "quote"
    #     slug = f"{base_slug}-{self.id}" if self.id else base_slug

    #     # Ensure uniqueness
    #     counter = 1
    #     while Text.objects.filter(slug=slug).exclude(id=self.id).exists():
    #         slug = f"{base_slug}-{self.id}-{counter}"
    #         counter += 1
    #     return slug

    # def save(self, *args, **kwargs):
    #     is_new = self.pk is None
    #     super().save(*args, **kwargs)  # Save once to get the ID

    #     if not self.slug or self.slug in ("", "none", "None", "None-None", f"{self.id}"):
    #         self.slug = self.generate_unique_slug()
    #         # Avoid infinite recursion: only save again if needed
    #         super().save(update_fields=["slug"])    
    
    
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
             
                        
    
    
    # slug = AutoSlugField(populate_from='generate_slug', unique=True, null=True, default=None)
    
    

    # # @property
    # # def slug_with_id(self):
    # #     return f"{self.slug}-{self.id}"
    

    # def save(self, *args, **kwargs):
    #     is_new = self.pk is None
    #     super().save(*args, **kwargs)  # Save once to get the ID    
        
    #     if not self.slug or self.slug in ("", "none", "None", "None-None", f"{self.id}"):
    #         self.slug = self.generate_slug()
    #         print(self.slug)
    #         # Avoid infinite recursion: only save again if needed
    #         super().save(update_fields=["slug"])                


    # def generate_slug(self):
    #     base_slug = slugify(self.text[:100])  # Normalisation de base
    #     slug = f"{base_slug}-{self.id}" 
    #     print(slug)
    #     # i = 1
    #     # while self.__class__.objects.filter(slug=slug).exists():
    #     #     slug = f"{base_slug}-{i}"
    #     #     i += 1
    #     # return slug
    #     return slug
    




    # def get_absolute_url(self):
    #     return f"/quote/{self.author.slug}/{self.slug}/"    
    
    # def generate_slug(self):
    #     # For quotes, include author name and ID for uniqueness
    #     if hasattr(self, 'author') and self.author:
    #         # Get the first 100 chars of the text, remove common words, and make it URL-friendly
    #         text_slug = self.text[:100].lower()
    #         # Remove common words and special characters
    #         text_slug = ' '.join(word for word in text_slug.split() if len(word) > 3)
    #         text_slug = ''.join(c for c in text_slug if c.isalnum() or c.isspace())
    #         text_slug = '-'.join(text_slug.split())
            
    #         # Combine with author name and ID
    #         author_slug = self.author.slug if hasattr(self.author, 'slug') else self.author.nickname.lower()
    #         return f"{author_slug}/{text_slug}-{self.id}"
    #     return self.text[:100]
    
    status = models.CharField(_('status'),max_length=10, choices=status_options, default='published')
    # objects = models.Manager() # Defaut Manager
    published = PublishedManager() # to make query preformated : Post.published.all() vs Post.objects.all()

    contributor = models.ForeignKey(
        User,
        related_name="%(app_label)s_%(class)s_related",
        related_query_name="%(app_label)s_%(class)ss",

        on_delete=models.SET_DEFAULT,
        # default=None
        default=default_contributor,
        null=True
        
        )


    
    

    # def save(self, *args, **kwargs):
    #     super().save(*args, **kwargs)  # First save to get `id`
    #     if not self.slug or not self.slug.endswith(str(self.id)):
    #         base_slug = slugify(self.text[:100])
    #         self.slug = f"{base_slug}-{self.id}"
    #         super().save(update_fields=['slug'])    
    
    # def get_absolute_url(self):
    #     return reverse('%(app_label)s:get-%(class)s', args=[self.slug])
    
    
    # def save(self, *args, **kwargs):
    #     # Calculate the value for the 'snippet' field by taking a slice of 'original_field'
    #     self.snippet = Substr(self.text, 1, 100)
    #     super().save(*args, **kwargs)

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
    
    class Meta:
        verbose_name_plural = "Categories"     
        ordering = ['title']        
        
     
