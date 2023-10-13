from django.db import models
from django.core.exceptions import ValidationError

from persons.users.models import User

import os

from django.conf import settings
LANGUAGES = settings.LANGUAGES

from django.db.models.functions import Substr


from django.urls import reverse
from autoslug import AutoSlugField



# from interactions.likes.models import Like
# from django.contrib.contenttypes.fields import GenericRelation
     

def default_contributor():
    admin_email = os.environ.get('ADMIN_EMAIL')
    return User.objects.get(email=admin_email)
    

class Text(models.Model):
    
    class PublishedManager(models.Manager):
        def get_queryset(self):
            return super().get_queryset() .filter(status='published')
        
    status_options = (
        ('draft', 'Draft'),
        ('published', 'Published')
    )
    
    text = models.TextField(max_length=1000) # max_length=500, default="Default value",  verbose_name="Text Content :"
    lang = models.CharField(max_length=2, choices=LANGUAGES, default="fr")
        
    # snippet = models.CharField(max_length=100, editable=False)
    
    slug = AutoSlugField(populate_from='generate_slug', unique=True, null=True, default=None)
    
    def generate_slug(self):
        # Customize this method to generate the slug from the desired field(s)
        return self.text[:100]
    
    status = models.CharField(max_length=10, choices=status_options, default='published')
    # objects = models.Manager() # Defaut Manager
    published = PublishedManager() # to make query preformated : Post.published.all() vs Post.objects.all()

    contributor = models.ForeignKey(
        User,
        related_name="%(app_label)s_%(class)s_related",
        related_query_name="%(app_label)s_%(class)ss",
        null=True,
        on_delete=models.SET_DEFAULT,
        default=None
        # default=default_contributor
        )

    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    
    
    # likes = models.ManyToManyField(
    #     User,
    #     # related_name="%(app_label)s_%(class)s_likes",
    #     default=None,
    #     blank=True,
    #     through='%(app_label)ss%(class)ssLikes'
    #     )
    
    


    # def get_absolute_url(self):
    #     return reverse('%(app_label)s:get-%(class)s', args=[self.slug])
    
    
    # def save(self, *args, **kwargs):
    #     # Calculate the value for the 'snippet' field by taking a slice of 'original_field'
    #     self.snippet = Substr(self.text, 1, 100)
    #     super().save(*args, **kwargs)

    
    # likes = GenericRelation(Like) # , related_query_names="quote"    
    # likes = models.ManyToManyField(User, related_name="%(app_label)s_%(class)s_likes")
    
    # def user_has_liked(self, user):
    #     return self.likes.filter(user=user).exists()    
    
    # def total_likes(self):
    #     return self.likes.count()

    class Meta:
        abstract = True
        ordering = ['date_created']


class Category(models.Model):
    title = models.CharField(max_length=100, verbose_name="Category Title :")
    # add snippet ?
    text = models.TextField(max_length=500, verbose_name=" Text :")
    slug = AutoSlugField(populate_from='title', unique=True, null=True, default=None)
    
    def __str__(self):
        return f'{self.title}'
    
    class Meta:
        verbose_name_plural = "Categories"     
