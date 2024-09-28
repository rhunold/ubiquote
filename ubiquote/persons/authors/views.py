
from django.shortcuts import render, get_object_or_404, redirect

import requests
import re
from django.utils.safestring import mark_safe

from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView

from django.http import JsonResponse
from django.contrib.auth.mixins import LoginRequiredMixin

from django.urls import reverse_lazy

from .models import Author, AuthorTranslation
from .forms import AuthorForm
from .forms import AuthorAutoCompleteForm

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

# from persons.authors.models import AuthorAutocomplete

from texts.quotes.models import Quote, QuotesLikes
from texts.quotes.forms import QuoteForm
# from texts.quotes.views import LanguageFilterMixin

# from texts.quotes.views import get_user_quotes_likes

from django.db.models import Q

from django.contrib.postgres.search import SearchVector, TrigramSimilarity
from django.contrib.postgres.lookups import Unaccent

from flexidate import parse
from django.conf import settings
LANGUAGES = settings.LANGUAGES
from django.utils.translation import get_language

from operator import itemgetter
from django.template.loader import render_to_string



class GetAuthorsView(ListView):
    model = Author
    template_name = 'get_authors.html'
    context_object_name = 'authors'
    paginate_by = settings.DEFAULT_PAGINATION
    api_url = 'http://127.0.0.1:8000/api/authors/'  
    

    def get(self, request, *args, **kwargs):
        page_number = request.GET.get('page', 1)
        search_query = request.GET.get('q', '')
        
        api_url = f'http://127.0.0.1:8000/api/authors/?page={page_number}&q={search_query}'
        response = requests.get(api_url)

        if response.status_code == 200:
            data = response.json()
            # print(type(data))
            # print(data)
            authors = data.get('results', [])
            count = data.get('count')            
            next_page_url = data.get('next')
        else:
            authors = []
            next_page_url = None

        if search_query:
            escaped_query = re.escape(search_query)
            for author in authors:
                author['highlighted_name'] = re.sub(
                    f'({escaped_query})', 
                    r'(<strong>\1</strong>)', 
                    author['fullname'], 
                    flags=re.IGNORECASE
                )
                author['highlighted_name'] = mark_safe(author['highlighted_name'])  # Mark safe for rendering HTML
        else:
            for author in authors:
                author['highlighted_name'] = author['fullname']

        # # Display author names along with their quote counts
        # for author in authors:
        #     author['display_name'] = f"{author['highlighted_name']} ({author['quote_count']} quotes)"



        context = {
            'authors': authors,
            'count': count,            
            'page_number': page_number,            
            'next_page_url': next_page_url,
            'search_query': search_query,
        }
        
        # Handle HTMX requests for partial rendering
        if request.headers.get('HX-Request'):  # Check for HTMX request
            return render(request, 'author_list.html', context)

        # For regular requests, render the full page
        return render(request, self.template_name, context)
    
    def render_to_response(self, context, **response_kwargs):
        if request.htmx:
            authors_html = render_to_string('author_list.html', context)
            print(authors_html)
            return JsonResponse({'authors_html': authors_html})
        else:
            return super().render_to_response(context, **response_kwargs)


  

# class GetAuthorsView(ListView):
#     model = Author
#     template_name = 'get_authors.html'
#     context_object_name = 'authors'
#     paginate_by = settings.DEFAULT_PAGINATION
#     api_url = 'http://127.0.0.1:8000/api/authors/'  

    

#     def get(self, request, *args, **kwargs):
#         page_number = request.GET.get('page', 1)
#         search_query = request.GET.get('q', '')
        
#         api_url = f'http://127.0.0.1:8000/api/authors/?page={page_number}&q={search_query}'
#         response = requests.get(api_url)

#         if response.status_code == 200:
#             data = response.json()
#             # print(type(data))
#             # print(data)
#             authors = data.get('results', [])
#             count = data.get('count')            
#             next_page_url = data.get('next')
#         else:
#             authors = []
#             next_page_url = None




#         # Highlight the search query in the author names if it exists
#         if search_query:
#             escaped_query = re.escape(search_query)
#             for author in authors:
#                 author['highlighted_name'] = re.sub(
#                     f'({escaped_query})', 
#                     r'<strong>\1</strong>', 
#                     author['fullname'], 
#                     flags=re.IGNORECASE
#                 )
#                 author['highlighted_name'] = mark_safe(author['highlighted_name'])  # Mark safe for rendering HTML
#         else:
#             for author in authors:
#                 author['highlighted_name'] = author['fullname']



#         context = {
#             'authors': authors,
#             'count': count,            
#             'page_number': page_number,            
#             'next_page_url': next_page_url,
#             'search_query': search_query,
#         }
        
#         # Handle HTMX requests for partial rendering
#         if request.headers.get('HX-Request'):  # Check for HTMX request
#             return render(request, 'author_list.html', context)

#         # For regular requests, render the full page
#         return render(request, self.template_name, context)
    
#     def render_to_response(self, context, **response_kwargs):
#         if request.htmx:
#             authors_html = render_to_string('author_list.html', context)
#             print(authors_html)
#             return JsonResponse({'authors_html': authors_html})
#         else:
#             return super().render_to_response(context, **response_kwargs)


  

class GetAuthorView(LoginRequiredMixin, ListView): # LanguageFilterMixin
    # model = Quote
    # queryset =  Quote.published.all()
    context_object_name = 'quotes'  
    template_name = 'get_author.html'
    paginate_by = settings.DEFAULT_PAGINATION  

    # def get_context_data(self, **kwargs):
    #     context = super().get_context_data(**kwargs)
    #     # context['quotes_count'] = self.get_queryset().count()        
        
    #     user = self.request.user
    #     quotes = context['quotes']  # Get the queryset of quotes
    #     quotes_like_statut = {quote.id: QuotesLikes.has_user_liked(user, quote) for quote in quotes}
    #     liked_quotes = [quote_id for quote_id, liked in quotes_like_statut.items() if liked]  
    #     context['liked_quotes'] = liked_quotes
        
    #     # Get the author slug from the URL parameter to Get the author object 
    #     author_slug = self.kwargs['slug']
    # #   context['author_slug'] = author_slug
    #     author = Author.objects.get(slug=author_slug)
    #     context['author'] = author

    #     return context


    def get(self, request, *args, **kwargs):
        page_number = request.GET.get('page', 1)
        
        author_slug = self.kwargs['slug']
        author = Author.objects.get(slug=author_slug)
        # print(author_slug)

        
        quote_api_url = f'http://127.0.0.1:8000/api/quotes/{author.slug}/?page={page_number}'
        quote_response = requests.get(quote_api_url)

        if quote_response.status_code == 200:
            data = quote_response.json()
            quotes = data.get('results', [])
            count = data.get('count')               
            next_page_url = data.get('next')
        else:
            quotes = []
            next_page_url = None
            
        author_api_url = f'http://127.0.0.1:8000/api/author/{author.slug}/'
        author_response = requests.get(author_api_url)

        if author_response.status_code == 200:
            author = author_response.json()
            # quotes = data.get('results', [])
            # next_page_url = data.get('next')
        else:
            author = []
            # next_page_url = None            

        context = {
            'author': author, 
            'quotes': quotes,
            'page_number': page_number,
            'count': count,                      
            'next_page_url': next_page_url,
            # 'search_query': search_query,                    
        }
        
        # If it's an HTMX request, return only the quotes part
        if request.htmx:

            return render(request, 'quotes_cards.html', context)        

        return render(request, self.template_name, context)    
    
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['has_user_liked'] = QuotesLikes.has_user_liked(self.request.user, self.object) 
        return context    
        
  
    def get_template_names(self):
        if self.request.htmx:
            return ['quotes_cards.html']
        return ['get_author.html']
        
  
 
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
        print(f"Received query: {query}")

        # Use Q objects to construct a complex OR query
        authors = Author.objects.filter(
            # Q(particul__iexact=query.strip()) |   
            # Q(nickname__unaccent__icontains=query) |
            # Q(last_name__unaccent__icontains=query) |
            # Q(first_name__unaccent__icontains=query) |
            # Q(middle_name__unaccent__icontains=query) 

            Q(fullname__unaccent__icontains=query)
        )


        # # Retrieve translated author names ?
        # translated_names = {}
        # for author in authors:
        #     translated_names[author.id] = author.get_translation(language_code='en')  # Replace 'en' with the desired language code

        # return render(request, 'author_list.html', {'authors': authors, })        # 'translated_names': translated_names

        # If it's an HTMX request, return only the quotes part
        if request.htmx:

            return render(request, 'author_list.html', {'authors': authors, 'translated_names': translated_names })        

        return render(request, self.template_name, context)


        # authors = Author.objects.annotate(similarity=TrigramSimilarity(Unaccent('last_name'), query),).filter(similarity__gt=0.3).order_by('-similarity')        
        print(authors.query)  # Check the generated SQL query

    else:
        # If the query is too short, return an empty result

        authors = Author.objects.all()[:10]        
        # authors = Author.objects.all().order_by( 'nickname', 'last_name')[:20]

        # # Retrieve translated author names
        # translated_names = {}
        # for author in authors:
        #     translated_names[author.id] = author.get_translation(language_code='en')  # Replace 'en' with the desired language code 
            
        # print("test X")       

        print(authors)
        return render(request, 'author_list.html', {'authors': authors, 'translated_names': translated_names }) # 'translated_names': translated_names   
  
  
def author_list(request):
  
    # authors = Author.objects.all()[:20]
    # authors = Author.objects.all().order_by('-last_name') 
    pass
     
    # return render(request, 'author_list.html', {'authors': authors})  
  