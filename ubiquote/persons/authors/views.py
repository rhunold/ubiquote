from django.shortcuts import render
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView

from django.http import JsonResponse
from django.contrib.auth.mixins import LoginRequiredMixin

from django.urls import reverse_lazy

from .models import Author, AuthorTranslation
from .forms import AuthorForm
from .forms import AuthorAutoCompleteForm

# from persons.authors.models import AuthorAutocomplete

from texts.quotes.models import Quote, QuotesLikes
from texts.quotes.forms import QuoteForm
from texts.quotes.views import LanguageFilterMixin

# from texts.quotes.views import get_user_quotes_likes

from django.db.models import Q

from django.contrib.postgres.search import SearchVector, TrigramSimilarity
from django.contrib.postgres.lookups import Unaccent

from flexidate import parse
from django.conf import settings
LANGUAGES = settings.LANGUAGES

class GetAuthorsView(ListView):
  model = Author
  template_name = 'get_authors.html'
  context_object_name = 'authors'
  # queryset =  Author.objects.all()  
  paginate_by = settings.DEFAULT_PAGINATION 
  

  def get_queryset(self):
      queryset = super().get_queryset()
      return queryset

  def get_context_data(self, **kwargs):
      context = super().get_context_data(**kwargs)
      
      # Check if the URL path contains "/en/"
      if '/en/' in self.request.path:
          # Get language code
          language_code = 'en'  # Default language code
          
          # Get translated names for authors
          translated_names = {}
          for author in context['authors']:
              author_translation = AuthorTranslation.objects.filter(author=author, language_code=language_code).first()
              if author_translation:
                  translated_names[author.id] = author_translation.translated_name
              # else:
              #     translated_names[author.id] = None


          context["translated_names"] = translated_names
          
          print(context["translated_names"] )

      return context  
  
  

  # def get_context_data(self, **kwargs):
  #     context = super().get_context_data(**kwargs)
  #     authors =  Author.objects.all()        
      
  #     # Retrieve translated author names
  #     translated_names = {}
  #     for author in authors:
  #         translated_names[author.id] = author.get_translation(language_code='en')  # Replace 'en' with the desired language code
          
  #     # print(translated_names)
  #     context["translated_names"] = translated_names

 
  #     return context  
  

class GetAuthorView(LoginRequiredMixin, LanguageFilterMixin, ListView):
  model = Quote
  queryset =  Quote.published.all()
  context_object_name = 'quotes'  
  template_name = 'get_author.html'
  paginate_by = settings.DEFAULT_PAGINATION  
  
  def get_context_data(self, **kwargs):
      context = super().get_context_data(**kwargs)
      
      user = self.request.user
      quotes = context['quotes']  # Get the queryset of quotes
      quotes_like_statut = {quote.id: QuotesLikes.has_user_liked(user, quote) for quote in quotes}
      liked_quotes = [quote_id for quote_id, liked in quotes_like_statut.items() if liked]  
      context['liked_quotes'] = liked_quotes
      
      # Get the author slug from the URL parameter to Get the author object 
      author_slug = self.kwargs['slug']
      author = Author.objects.get(slug=author_slug)
      context['author'] = author
      
      # Get translated names for authors
      if hasattr(self, 'request'):
          language_code = self.request.LANGUAGE_CODE
      else:
          language_code = 'en'  # Default language if language code is not available
      
      translated_names = {}
      for quote in quotes:
          author = quote.author
          if author:
              translated_names[quote.id] = author.get_translation(language_code)
          else:
              translated_names[quote.id] = 'Unknown'
      
      context['translated_names'] = translated_names
      
      first_result = next(iter(translated_names.values()), None)
      context['translated_name'] = first_result
      
      
      from datetime import datetime, timedelta
      if author.date_birth_datefield  is not None:
        author.date_birth_datefield = author.date_birth_datefield +timedelta(days=10)
        # print(author.date_birth_datefield)
      else:
        print("operation impossible")

 
      return context
  
  
  
 
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
            # Q(particul__iexact=query.strip()) |   
            # Q(nickname__unaccent__icontains=query) |
            # Q(last_name__unaccent__icontains=query) |
            # Q(first_name__unaccent__icontains=query) |
            # Q(middle_name__unaccent__icontains=query) 

            Q(fullname__unaccent__icontains=query)
        )
        
        print(authors)

        # Retrieve translated author names
        translated_names = {}
        for author in authors:
            translated_names[author.id] = author.get_translation(language_code='en')  # Replace 'en' with the desired language code
            
        print(authors)
        

        return render(request, 'author_list.html', {'authors': authors, 'translated_names': translated_names})        
        
        # authors = Author.objects.annotate(similarity=TrigramSimilarity(Unaccent('last_name'), query),).filter(similarity__gt=0.3).order_by('-similarity')        
        

        # print(authors.query)  # Check the generated SQL query

    else:
        # If the query is too short, return an empty result


        
        authors = Author.objects.all()[:20]        
        # authors = Author.objects.all().order_by( 'nickname', 'last_name')[:20]
        
        
        # Retrieve translated author names
        translated_names = {}
        for author in authors:
            translated_names[author.id] = author.get_translation(language_code='en')  # Replace 'en' with the desired language code 
            
        print("test X")       
    
        return render(request, 'author_list.html', {'authors': authors, 'translated_names': translated_names})
  
  
def author_list(request):
  
    # authors = Author.objects.all()[:20]
    # authors = Author.objects.all().order_by('-last_name') 
    pass
     
    # return render(request, 'author_list.html', {'authors': authors})  
  