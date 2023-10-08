from django.db import models

from persons.authors.models import Author
from ..models import Category, Text

from django.urls import reverse
  

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
        return reverse('quotes:get-quotes')
    

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
