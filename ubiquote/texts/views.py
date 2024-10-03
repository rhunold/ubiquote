import random
from django.shortcuts import render

from django.utils.translation import gettext as _
from django.utils.translation import get_language, activate
from django.db.models import Count, Prefetch

from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required

from django.http import HttpResponseRedirect, Http404

from django.urls import reverse_lazy, reverse
from django.shortcuts import get_object_or_404

from .models import Category
from texts.quotes.models import Quote, QuotesLikes
from django.views.generic import ListView, DetailView  # CreateView, UpdateView, DeleteView
from texts.mixins import DataFetchingMixin, TokenRefreshMixin 

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from django.conf import settings
LANGUAGES = settings.LANGUAGES
from django.utils.translation import get_language

import requests

from rest_framework.permissions import AllowAny

# from texts.quotes.services import RecommendationService


class GetCategoriesView(ListView):
    template_name = 'get_categories.html'
    context_object_name = 'categories'  
    paginate_by = settings.DEFAULT_PAGINATION 
    api_url = 'http://127.0.0.1:8000/api/categories/'
    

    # def get_context_data(self, **kwargs):
    #     context = super().get_context_data(**kwargs)
    #     return context
    

    def get(self, request, *args, **kwargs):
        page_number = request.GET.get('page', 1)
        search_query = request.GET.get('q', '')
        
        api_url = f'{self.api_url}?page={page_number}&q={search_query}'
        response = requests.get(api_url)

        if response.status_code == 200:
            data = response.json()  
            categories = data.get('results', [])
            count = data.get('count')               
            next_page_url = data.get('next')
            
        else:
            categories = []
            # next_page_url = None

        context = {
            'categories': categories,
            'count': count,            
        }

        return render(request, self.template_name, context)
        



class GetCategoryView(DataFetchingMixin, ListView):
    template_name = 'get_category.html'
    api_url = settings.API_URL


    def get(self, request, *args, **kwargs):
        page_number = request.GET.get('page', 1)
        category_slug = self.kwargs['slug']

        # Fetch quotes of the author
        quotes_data = self.get_api_data(page_number, endpoint=f'category/{category_slug}/quotes/')
        category_data = self.get_api_data(page_number, endpoint=f'category/{category_slug}/')


        # Handle pagination for quotes
        quotes = quotes_data.get('results', [])
        next_page_url = quotes_data.get('next')
        previous_page_url = quotes_data.get('previous')
        count = quotes_data.get('count', 0)

        # overide url generation to fit this special case
        lang = request.LANGUAGE_CODE        
        if next_page_url:
            next_page_url = next_page_url.replace(f'/api/category/{category_slug}/quotes/', f'/{lang}/category/{category_slug}/')

        if previous_page_url:
            previous_page_url = previous_page_url.replace(f'/api/category/{category_slug}/quotes/', f'/{lang}/category/{category_slug}/')    

        context = {
            'category': category_data,
            'quotes': quotes,
            'count': count,
            'page_number': page_number,
            'next_page_url': next_page_url,
            'previous_page_url': previous_page_url,
            
        }
        return self.render_htmx_or_full_quotes(request, context)



class HomeView(DataFetchingMixin, ListView):
    template_name = 'home.html'
    api_url = settings.API_URL


    def get(self, request, *args, **kwargs):
        page_number = request.GET.get('page', 1)

        # Fetch data for the home view (e.g., recommendations)
        data = self.get_api_data(page_number, endpoint='')  # Custom endpoint for HomeView

        # Handle pagination and results
        results = data.get('results', [])
        next_page_url, previous_page_url = self.process_pagination(data, request)
        count = data.get('count', 0)

        context = {
            'quotes': results,  # Keep this as 'quotes' if your template expects it
            'count': count,
            'page_number': page_number,
            'next_page_url': next_page_url,
            'previous_page_url': previous_page_url,
        }
        return self.render_htmx_or_full_quotes(request, context)


# def translate(language):
#   cur_language = get_language()
#   try:
#     activate(language)
#     text = _('hello')
#   finally:
#     activate(cur_language)
#   return text
  

# # https://stackoverflow.com/a/66271685
# def get_nationality():
#   nat = Author.objects.get(id=1)
#   return _(nat.nationality)