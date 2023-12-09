from django.shortcuts import render
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView

from django.http import JsonResponse

from django.urls import reverse_lazy

from .models import Author
from .forms import AuthorForm
from .forms import AuthorAutoCompleteForm

# from persons.authors.models import AuthorAutocomplete

from texts.quotes.models import Quote
from texts.quotes.forms import QuoteForm

from texts.quotes.views import get_user_quotes_likes

from django.db.models import Q

from django.contrib.postgres.search import SearchVector, TrigramSimilarity
from django.contrib.postgres.lookups import Unaccent
# from django.db.models.functions import Unaccent 
# from django.db.models.functions import Lower
# from django.contrib.postgres.lookups import Unaccent
# from django.core.paginator import Paginator


class GetAuthorsView(ListView):
  model = Author
  template_name = 'get_authors.html'
  context_object_name = 'authors'
  # ordering =['nickname', 'last_name']
  paginate_by = 20
  
  # def get_context_data(self, **kwargs):
  #     context = super().get_context_data(**kwargs)
  #     context['autocomplete_url'] = 'author-autocomplete'
  #     return context
  
  queryset = Author.objects.all()
  
  

  
  
  # form_class = AuthorAutoCompleteForm  
  
  # def get_queryset(self):
  #   query = self.request.GET.get('q')
  #   if query:
  #       return  Author.objects.annotate(search=SearchVector('first_name', 'last_name', 'middle_name', 'nickname'),).filter(search=query)

  #   else:
  #       return Author.objects.all()
  
  
  # def get_queryset(self):
  #     query = self.request.GET.get("q")
  #     return Author.objects.annotate(search=SearchVector("last_name", "nickname")).filter(
  #         search=query
  #     )  


class GetAuthorView(ListView):
  # model = Author
  model = Quote
  queryset = Quote.published.all().order_by('slug')
  context_object_name = 'quotes'  
  template_name = 'get_author.html'
  
  def get_context_data(self, **kwargs):
      context = super().get_context_data(**kwargs)
      
      # Get user likes for buton status
      get_user_quotes_likes(self, context)      
      
      # Get the author slug from the URL parameter to Get the author object 
      author_slug = self.kwargs['slug']
      author = Author.objects.get(slug=author_slug)
      context['author'] = author
 
      return context

  def get_queryset(self):
      # Get the category id from the URL parameter
      author_slug = self.kwargs['slug']
      
      # Filter quotes by the manager and same author slug
      queryset = Quote.published.filter(author__slug=author_slug) 
      
      return queryset
    
    

  # def get_context_data(self, **kwargs):
  #   context = super().get_context_data(**kwargs)
  #   quotes = Quote.published.all()
  #   quotes_count = Quote.published.count()    

  #   # Create a dictionary to store the likes status for each quote
  #   liked_quotes = {}
    
  #   for quote in self.queryset:
  #     liked_quotes[quote.id] = False  # Initialize to False by default


  #     if quote.likes.filter(id=self.request.user.id).exists():
  #       liked_quotes[quote.id] = True

  #       print(liked_quotes)

  #   context['quotes'] = quotes
  #   context['quotes_count'] = quotes_count
  #   context['liked_quotes'] = liked_quotes  # Pass the like status dictionary to the template
    
    
  
 
class AddAuthorView(CreateView):
  model = Author
  form_class = AuthorForm
  template_name = 'add_author.html'
  def get_success_url(self):
      # Redirect to the detail page of the newly created author
      return reverse_lazy('authors:get-author', kwargs={'slug': self.object.slug})
  # fields = '__all__'
  

  
class UpdateAuthorView(UpdateView):
  model = Author
  form_class = AuthorForm
  template_name = 'update_author.html'
  # fields = '__all__'  
  def get_success_url(self):
      # Redirect to the detail page of the newly created author
      return reverse_lazy('authors:get-author', kwargs={'slug': self.object.slug})
  
class DeleteAuthorView(DeleteView):
  model = Author
  # form_class = QuoteForm
  template_name = 'delete_author.html'
  success_url = reverse_lazy('author:get-authors')
  # fields = '__all__'  


def search_authors(request):
    query = request.GET.get('q', '')


    # Check if the query has a minimum length of 2 characters
    if len(query) >= 2:
        # print(f"Received query: {query}")

        # Use Q objects to construct a complex OR query
        authors = Author.objects.filter(
            Q(nickname__unaccent__icontains=query) |
            Q(last_name__unaccent__icontains=query) |
            Q(first_name__unaccent__icontains=query) |
            Q(middle_name__unaccent__icontains=query) 
        )

        return render(request, 'author_list.html', {'authors': authors})        
        
        # authors = Author.objects.annotate(similarity=TrigramSimilarity(Unaccent('last_name'), query),).filter(similarity__gt=0.3).order_by('-similarity')        
        

        # print(authors.query)  # Check the generated SQL query

    else:
        # If the query is too short, return an empty result

        
        authors = Author.objects.all()[:5]        
        # authors = Author.objects.all().order_by( 'nickname', 'last_name')[:20]
    
        return render(request, 'author_list.html', {'authors': authors})
  
  
def author_list(request):
  
  
  
  
    # authors = Author.objects.all()[:20]
    # authors = Author.objects.all().order_by('-last_name') 
    pass
     
    # return render(request, 'author_list.html', {'authors': authors})  
  