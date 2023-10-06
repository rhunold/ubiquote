from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError

import os

from .constants import SEX_CHOICES, NATIONALITIES_CHOICES

from django.conf import settings
LANGUAGES = settings.LANGUAGES

from .overrides import UserManager

from django.urls import reverse


class Person(models.Model):
    first_name = models.CharField(max_length=30, null=True, blank=True)
    middle_name = models.CharField(max_length=30, null=True, blank=True)
    last_name = models.CharField(max_length=30, null=True, blank=True)

    date_birth = models.DateField('birthday', null=True, blank=True)
    date_death = models.DateField('death', null=True, blank=True)
    
    sex = models.CharField(max_length=1,choices=SEX_CHOICES, null=True, blank=True)
    nationality = models.CharField(choices=NATIONALITIES_CHOICES, null=True, blank=True)

    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)    

    twitter_url = models.URLField(max_length=200, null=True, blank=True, default='http://www.twitter.com/')
    instagram_url = models.URLField(max_length=200, null=True, blank=True, default='http://www.instagram.com/')
    facebook_url = models.URLField(max_length=200, null=True, blank=True, default='http://www.facebook.com/')

    class Meta:
        abstract = True


class User(AbstractUser, Person):
    username = models.CharField(max_length=30)
    email = models.EmailField(verbose_name='email address', max_length=255, unique=True)
    # client = models.BooleanField(default=False, blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username',]
    objects = UserManager()
    
    def __str__(self):
        return f'{self.username}'




class Author(Person):
    nickname = models.CharField(max_length=30, null=True, blank=True)
    biography = models.TextField(max_length=500, blank=True, verbose_name="Biography :")
    
    def __str__(self):
        if self.nickname is not None:
            return f'{self.nickname}'
        else:
            return f'{self.first_name or ""} {self.middle_name or ""} {self.last_name or ""}'
            

def default_contributor():
    admin_email = os.environ.get('ADMIN_EMAIL')
    return User.objects.get(email=admin_email)
    

class Text(models.Model):
    text = models.TextField(max_length=500, verbose_name="Text Content :") #, default="Default value"
    lang = models.CharField(max_length=2, choices=LANGUAGES, default="fr")

    contributor = models.ForeignKey(
        User,
        related_name="%(app_label)s_%(class)s_related",
        related_query_name="%(app_label)s_%(class)ss",
        # on_delete=models.CASCADE,        

        null=True,
        on_delete=models.SET_DEFAULT,
        default=default_contributor
        )

    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    

    class Meta:
        abstract = True
        ordering = ['date_created']


class Category(models.Model):
    title = models.CharField(max_length=100, verbose_name="Category Title :")
    text = models.TextField(max_length=500, verbose_name=" Text :")
    # slug = models.SlugField(max_length=100, verbose_name="Category Slug :")
    
    def __str__(self):
        return f'{self.title}'
    
    class Meta:
        verbose_name_plural = "Categories"     
        
        

class Quote(Text):
    author = models.ForeignKey(Author, null=True, blank=True, on_delete=models.CASCADE) #, default=1)

    categories = models.ManyToManyField(
        Category,
        # related_query_name="%(app_label)s_%(class)ss",        
        # related_name="%(app_label)s_%(class)s_related",        
        # blank=True,
        # default=None,
        through='QuoteCategory',
        # validators=[validate_categories_count]
        )
    
    # def default_author(self):
    #     return Author.objects.get(id=1)    

    def get_categories(self):
        return "\n".join([cat.title for cat in self.categories.all()])    

    def __str__(self):
        return f'"{self.text[:100]}" - Author : {self.author}'
    
    def get_absolute_url(self):
        return reverse('texts:get-quotes')
    

    # def add_categories(self, category_instance):
    #     QuoteCategory.objects.create(quote=self, category=category_instance)    
    
    

class QuoteCategory(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    quote = models.ForeignKey(Quote, on_delete=models.CASCADE)
    
    class Meta:
        constraints = [
            # models.CheckConstraint(
            #     # check=models.Q(quote__count__lte=3,),
            #     check=models.Q(quote__count__lte=3,),                
            #     name='check_categorize_per_quote'
            # ),
            models.UniqueConstraint(
                name="%(app_label)s_%(class)s_unique_relationships",
                fields=["quote", "category"],
            ),    
        ]  
