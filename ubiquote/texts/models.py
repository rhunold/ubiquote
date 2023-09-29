from django.db import models
from django.contrib.auth.models import AbstractUser

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

    twitter_url = models.URLField(max_length=200, null=True, blank=True, default='http://www.twitter.com/')
    instagram_url = models.URLField(max_length=200, null=True, blank=True, default='http://www.instagram.com/')
    facebook_url = models.URLField(max_length=200, null=True, blank=True, default='http://www.facebook.com/')

    class Meta:
        abstract = True


class User(AbstractUser, Person):
    username = models.CharField(max_length=30)
    # username = None
    email = models.EmailField(verbose_name='email address', max_length=255, unique=True)
    client = models.BooleanField(default=False, blank=True)

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
    return lambda: User.objects.get(email=os.environ.get('ADMIN_EMAIL'))

class Text(models.Model):
    text = models.TextField(max_length=500, verbose_name="Text Content :")
    lang = models.CharField(max_length=2, choices=LANGUAGES, default="fr")

    contributor = models.ForeignKey(
        User,
        related_name="%(app_label)s_%(class)s_related",
        related_query_name="%(app_label)s_%(class)ss",
        on_delete=models.SET_DEFAULT,
        null=True,
        # default=None,
        default=default_contributor
        )

    date_created = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        abstract = True
        ordering = ['date_created']


def default_author():
    return lambda: Author.objects.get(id=2)
    
class Quote(Text):
    # user = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE)
    author = models.ForeignKey(Author, null=True, blank=True, on_delete=models.CASCADE, default = default_author)    # , default=lambda: Author.objects.get(id=1)
    # category = models.ManyToManyField(Category)
    # source = models.ForeignKey(Source, null=True, blank=True, on_delete=models.CASCADE)

    # @staticmethod
    # def get_absolute_url():
    #     return reverse("create_quote")

    # def display_category(self):
    #     return ', '.join([cat.title for cat in self.category.all()])

    def __str__(self):
        return f'"{self.text[:100]}" - Author : {self.author}'
    
    def get_absolute_url(self):
        # return reverse('texts:get-quote', args=(self.id,))
        return reverse('texts:get-quotes')    

# class Category(models.Model):
#     title = models.CharField(max_length=100, verbose_name="Category Title :")
#     # slug = models.SlugField(max_length=100, verbose_name="Category Slug :")

#     @staticmethod
#     def get_absolute_url():
#         return reverse("create_category")

#     def __str__(self):
#         return self.title