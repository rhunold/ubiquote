from django.db import models

from persons.authors.models import Author
from django.contrib.auth.models import AnonymousUser
from persons.users.models import User
from texts.models import Text, Category

from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from django.db.models.signals import pre_delete
from django.dispatch import receiver

from texts.mixins import CleaningMixin

from .utils import generate_response
from django.db import transaction


# from django_pgvector.fields import VectorField

# from django_elasticsearch_dsl import Document
# from django_elasticsearch_dsl.registries import registry



class Quote(Text):
    author = models.ForeignKey(Author, null=True, blank=True, on_delete=models.CASCADE, related_name='author') #, default=1)
    
    
    # work = models.ForeignKey(Work, on_delete=models.SET_NULL, null=True, blank=True)
    
    # tfidf_vector = VectorField()    

    categories = models.ManyToManyField(
        Category,
        # related_query_name="%(app_label)s_%(class)ss",        
        # related_name="%(app_label)s_%(class)s_related",        
        blank=True,
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


    dimensions = models.JSONField(null=True, blank=True)  # ou models.JSONField avec Django >= 3.1

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
    
    
    def save(self, *args, enrich=True, **kwargs):
        if enrich:
            # is_new = self.pk is None
            super().save(*args, **kwargs)  # First save to get the ID
            
            if not self.dimensions:
                insights = generate_response(self.text)
                # super().save(update_fields=["dimensions", ])   
                
                # Gestion des dimensions
                self.dimensions = {
                    k: v for k, v in insights.items() if k != "categories"
                }                
                # Sauvegarde des dimensions
                super().save(update_fields=["dimensions"])
        
                # Gestion des catégories
                categories = []
                if "categories" in insights:
                    for cat_name in insights["categories"]:
                        cat, _ = Category.objects.get_or_create(
                            title__iexact=cat_name.strip(),
                            defaults={"title": cat_name.strip()}
                        )
                        categories.append(cat)



                # Ajout des catégories après sauvegarde
                if categories:
                    self.categories.set(categories)
                    
    
    class Meta:
        ordering = ['-date_created'] 
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

# # Save all instance to generate the new slug
# for quote in Quote.objects.all():
#     quote.save()


class QuoteRaw(Text, CleaningMixin):  # hérite de text, lang, date_created
    author = models.ForeignKey(Author, null=True, blank=True, on_delete=models.CASCADE, related_name='raw_author') #, default=1)


    processed = models.BooleanField(default=False)  # Marque comme traité ou non


    def __str__(self):
        return f'"{self.text[:100]}" - Raw Author : {self.author}'

    def save(self, *args, **kwargs):
        self.clean_fields()
        super().save(*args, **kwargs)

    class Meta:
        ordering = ['-date_created']

class QuotesCategories(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    quote = models.ForeignKey(Quote, on_delete=models.CASCADE)
    
    class Meta:
        # ordering = ['category']    
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
    quote = models.ForeignKey(Quote, on_delete=models.CASCADE) # related_name='likes'
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
          

class UserQuoteRecommendation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    quote = models.ForeignKey('Quote', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    show_count = models.PositiveIntegerField(default=0)  # Track how many times shown

    def __str__(self):
        return f"Recommendation for {self.user.username} (Quote ID: {self.quote.id})"
    
    
    # class Meta:
    #     constraints = [
    #         models.UniqueConstraint(
    #             name="%(app_label)s_%(class)s_unique_relationships",
    #             fields=["quote", "user"],
    #         ),    
    #     ]
    #     indexes = [
    #             # models.Index(fields=['user',]),           
    #             models.Index(fields=['user', 'quote']),
    #         ]       
