from django.db import models
from autoslug import AutoSlugField

from django.contrib.auth.models import AbstractUser
# from .overrides import UserManager

from ..models import Person

# from texts.quotes.models import Quote


class User(AbstractUser, Person):
    username = models.CharField(max_length=30)
    email = models.EmailField(verbose_name='email address', max_length=255, unique=True)
    # client = models.BooleanField(default=False, blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username',]

    slug = AutoSlugField(populate_from='username', unique=True, null=True, default=None)
    
    avatar = models.ImageField(upload_to='avatars/users/', null=True, blank=True, default='avatars/default.png')
    
    # recommended_quotes = models.TextField(null=True, blank=True)
    
    # recommended_quotes = models.ManyToManyField(
    #     Quote,
    #     through='QuotesRecommanded',
    #     # related_name="quotesrecommanded"
    #     )   
        
        
    
    
    # # A mettre dans le model User (donc mettre Quote dans le champs M2M) et à renommer en quote_likes => copy past ou avant de vider bdd et recommancer import csv
    # likes = models.ManyToManyField(
    #     Quote,
    #     through='QuotesLikes',
    #     # related_name="quoteslikes"
    #     )   
        
    
    # following_users = models.ManyToManyField(
    #     User,
    #     # through='UsersFollowings',
    #     # related_name="users_followings"
    #     )
    
    
    # following_authors= models.ManyToManyField(
    #     Author,
    #     # through='AuthorsFollowings',
    #     # related_name="authors_followings"
    #     )    
    
    # following_categories = models.ManyToManyField(
    #     Category,
    #     # through='CategoriesFollowings',
    #     # related_name="categories_following"
    #     )    
    
    # quotes_history = models.ManyToManyField(
    #     Quote,
    #     # through='QuotesHistory',
    #     # related_name="quotes_history"
    #     )
    
    # quotes_liked= models.ManyToManyField(
    #     Quote,
    #     # through='QuotesLikeds',
    #     # related_name="quotes_likeds"
    #     )       
    
    # time_in_app => track amount of time the user is using the service.
    
    # for_you_algo_profile => generate a ML algo on differents user preference and information to match the best content (quote.). 
    # exlusion_for_you_algo_profile => a filter on for_you_algo_profile if the for_you_algo_profile must be generate by a cron (so if I unfollow a user, I may see its quote for a while until my for_you_algo_profile has been updated)
                   
            
        
    # objects = UserManager()
    
    def __str__(self):
        return f'{self.username}'
    
    # class Meta:
    #     app_label = "user" 
    
