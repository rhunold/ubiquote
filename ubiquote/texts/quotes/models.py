from django.db import models

from persons.authors.models import Author
from persons.users.models import User
from ..models import Category, Text

from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from django.db.models.signals import pre_delete
from django.dispatch import receiver


class Quote(Text):
    author = models.ForeignKey(Author, null=True, blank=True, on_delete=models.CASCADE, related_name='author') #, default=1)

    categories = models.ManyToManyField(
        Category,
        # related_query_name="%(app_label)s_%(class)ss",        
        # related_name="%(app_label)s_%(class)s_related",        
        # blank=True,
        # default=None,
        through='QuotesCategories',
        # validators=[validate_categories_count]
        )
    
    likes = models.ManyToManyField(
        User,
        through='QuotesLikes',
        )     
    
    # def default_author(self):
    #     return Author.objects.get(id=1)
    
    def count_likes(self):
        return self.likes.all().count()

    def get_categories(self):
        return "\n".join([cat.title for cat in self.categories.all()])    

    def __str__(self):
        return f'"{self.text[:100]}" - Author : {self.author}'
    
    # def get_absolute_url(self):
    #     return reverse('quotes:get-quote') #, args=[self.slug]
    

    # def add_categories(self, category_instance):
    #     QuoteCategory.objects.create(quote=self, category=category_instance)   



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
    
    class Meta:
        constraints = [
            models.UniqueConstraint(
                name="%(app_label)s_%(class)s_unique_relationships",
                fields=["quote", "user"],
            ),    
        ]      
    