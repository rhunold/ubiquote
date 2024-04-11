from django.db import models

from persons.authors.models import Author
from django.contrib.auth.models import AnonymousUser
from persons.users.models import User
from texts.models import Text, Category

from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from django.db.models.signals import pre_delete
from django.dispatch import receiver

# from django_pgvector.fields import VectorField

# from django_elasticsearch_dsl import Document
# from django_elasticsearch_dsl.registries import registry



class Quote(Text):
    author = models.ForeignKey(Author, null=True, blank=True, on_delete=models.CASCADE, related_name='author') #, default=1)
    
    # tfidf_vector = VectorField()    

    categories = models.ManyToManyField(
        Category,
        # related_query_name="%(app_label)s_%(class)ss",        
        # related_name="%(app_label)s_%(class)s_related",        
        # blank=True,
        # default=None,
        through='QuotesCategories',
        # validators=[validate_categories_count]
        )
    
    
    # A mettre dans le model User (donc mettre Quote dans le champs M2M) et à renommer en quote_likes => copy past ou avant de vider bdd et recommancer import csv
    likes = models.ManyToManyField(
        User,
        through='QuotesLikes',
        # related_name="quoteslikes"
        )   

    # for_you_algo_feature => generate a value to match with user.for_you value => give the user the content that is the most accurate to his preference/consomation/interests...    
    
    # def default_author(self):
    #     return Author.objects.get(id=1)
    
    # def count_likes(self):
    #     return self.likes.all().count()
    
    # def get_total_likes(self):
    #     return self.likes.count()

    # def has_user_liked(self, user):
    #     return self.likes.filter(user=user).exists()
    

    def get_categories(self):
        return "\n".join([cat.title for cat in self.categories.all()])    

    def __str__(self):
        return f'"{self.text[:100]}" - Author : {self.author}'
    
    # def get_absolute_url(self):
    #     return reverse('quotes:get-quote') #, args=[self.slug]
    

    # def add_categories(self, category_instance):
    #     QuoteCategory.objects.create(quote=self, category=category_instance)  
    
    class Meta:
        # ordering =['-date_created'],
        indexes = [
                models.Index(fields=['-date_created','text','author'], name='quotes_idx',)
            
            
                # models.Index(fields=['text',]),           
                # models.Index(fields=['author',]),
                # models.Index(fields=['lang',]),             
                # models.Index(fields=['categories',]),
                # models.Index(fields=['-date_created', ]),
                # models.Index(fields=['slug',]),               
                # contributor
                # status
                # published
                # slug
                # date_created
                # date_updated
            ]             



class QuotesCategories(models.Model):
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



    
class QuotesLikes(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    quote = models.ForeignKey(Quote, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    # @classmethod
    # def has_user_liked(cls, user, quote):
    #     return cls.objects.filter(user=user, quote=quote).exists()
    
    @classmethod
    def has_user_liked(cls, user, quote):
        if not isinstance(user, User) or isinstance(user, AnonymousUser):
            return False  # Return False if user is not authenticated or is anonymous
        return cls.objects.filter(user=user, quote=quote).exists()    
    
    # @classmethod
    # def total_likes_by_user(cls, user):
    #     return cls.objects.filter(user=user).count()    
    
    class Meta:
        constraints = [
            models.UniqueConstraint(
                name="%(app_label)s_%(class)s_unique_relationships",
                fields=["quote", "user"],
            ),    
        ]
        indexes = [
                # models.Index(fields=['user',]),           
                models.Index(fields=['user', 'quote']),
            ]           
          

