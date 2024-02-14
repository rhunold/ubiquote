from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from persons.users.models import User

import os

from django.conf import settings
LANGUAGES = settings.LANGUAGES

from django.db.models.functions import Substr


from django.urls import reverse
from autoslug import AutoSlugField

     

def default_contributor():
    admin_email = os.environ.get('ADMIN_EMAIL')
    try:
        return User.objects.get(email=admin_email).id
    except User.DoesNotExist:
        # Gérer le cas où l'utilisateur n'existe pas
        return None
    

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
    
    text = models.TextField(_('Text'), max_length=1000) # max_length=500, default="Default value",  verbose_name="Text Content :"
    lang = models.CharField(_('Langs'), max_length=2, choices=LANGUAGES, default="fr")
        
    # snippet = models.CharField(max_length=100, editable=False)
    
    slug = AutoSlugField(populate_from='generate_slug', unique=True, null=True, default=None)
    
    def generate_slug(self):
        # Customize this method to generate the slug from the desired field(s)
        return self.text[:100]
    
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

    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    
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
        
     
