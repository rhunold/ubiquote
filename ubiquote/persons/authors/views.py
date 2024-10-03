
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
# from texts.quotes.views import BaseQuoteAPIListView

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

# from persons.authors.models import AuthorAutocomplete

from texts.quotes.models import Quote, QuotesLikes
from texts.quotes.forms import QuoteForm
# from texts.quotes.views import LanguageFilterMixin

from texts.mixins import DataFetchingMixin, TokenRefreshMixin # DatasFetchingMixin

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


class GetAuthorsView(DataFetchingMixin, ListView):
    template_name = 'get_authors.html'
    api_url = settings.API_URL
    

    def get(self, request, *args, **kwargs):
        page_number = request.GET.get('page', 1)
        search_query = request.GET.get('q', '')        

        # Fetch data for the home view (e.g., recommendations)
        data = self.get_api_data(page_number, endpoint='authors/', search_query=search_query)  # Custom endpoint for GetAuthorsView

        # Handle pagination and results
        authors = data.get('results', [])
        next_page_url, previous_page_url = self.process_pagination(data, request)
        count = data.get('count', 0)


        if search_query:
            escaped_query = re.escape(search_query)
            for author in authors:
                author['highlighted_name'] = re.sub(
                    f'({escaped_query})', 
                    r'(<strong>\1</strong>)', 
                    author['fullname'], 
                    flags=re.IGNORECASE
                )
                author['highlighted_name'] = mark_safe(author['highlighted_name'])
        else:
            for author in authors:
                author['highlighted_name'] = author['fullname']

        context = {
            'authors': authors,  
            'count': count,
            'page_number': page_number,
            'next_page_url': next_page_url,
            'previous_page_url': previous_page_url,
            'search_query': search_query,
        }
        return self.render_htmx_or_full_authors(request, context)
    

    
#     # Deal if javascript off
#     def render_to_response(self, context, **response_kwargs):
#         if request.htmx:
#             authors_html = render_to_string('author_list.html', context)
#             # print(authors_html)
#             return JsonResponse({'authors_html': authors_html})
#         else:
#             return super().render_to_response(context, **response_kwargs)



class GetAuthorView(DataFetchingMixin, ListView):
    template_name = 'get_author.html'
    api_url = settings.API_URL
    

    def get(self, request, *args, **kwargs):
        page_number = request.GET.get('page', 1)
        author_slug = self.kwargs['slug']

        # Fetch quotes of the author
        quotes_data = self.get_api_data(page_number, endpoint=f'author/quotes/{author_slug}/')
        author_data = self.get_api_data(page_number=0, endpoint=f'author/{author_slug}/')


        # Handle pagination for quotes
        quotes = quotes_data.get('results', [])
        next_page_url = quotes_data.get('next')
        previous_page_url = quotes_data.get('previous')
        count = quotes_data.get('count', 0)
        
        
        # overide url generation to fit this special case
        lang = request.LANGUAGE_CODE
        if next_page_url:
            next_page_url = next_page_url.replace(f'/api/author/quotes/{author_slug}/', f'/{lang}/author/{author_slug}/')
        if previous_page_url:
            previous_page_url = previous_page_url.replace(f'/api/author/quotes/{author_slug}/', f'/{lang}/author/{author_slug}/')    

        context = {
            'author': author_data,
            'quotes': quotes,
            'count': count,
            'page_number': page_number,
            'next_page_url': next_page_url,
            'previous_page_url': previous_page_url,
            
        }
        return self.render_htmx_or_full_quotes(request, context)


        
  
 
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
        # print(authors.query)  # Check the generated SQL query

    else:
        # If the query is too short, return an empty result

        authors = Author.objects.all()[:10]        
        # authors = Author.objects.all().order_by( 'nickname', 'last_name')[:20]

        # # Retrieve translated author names
        # translated_names = {}
        # for author in authors:
        #     translated_names[author.id] = author.get_translation(language_code='en')  # Replace 'en' with the desired language code 
            
        # print("test X")       

        # print(authors)
        return render(request, 'author_list.html', {'authors': authors }) # 'translated_names': translated_names   
  
  

  