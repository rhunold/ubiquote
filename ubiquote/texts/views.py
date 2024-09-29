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
# from texts.quotes.views import LanguageFilterMixin
# from texts.quotes.views import get_user_quotes_likes
from django.views.generic import ListView, DetailView  # CreateView, UpdateView, DeleteView

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
    

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        return context
    

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
            # 'page_number': page_number,            
            # 'next_page_url': next_page_url,
            # 'search_query': search_query,
        }
    
        
        # If it's an HTMX request, return only the quotes part
        # if request.htmx:

        #     return render(request, 'quotes_cards.html', context)        

        return render(request, self.template_name, context)
        


class GetCategoryView(ListView): #LanguageFilterMixin
    context_object_name = 'quotes'
    template_name = 'get_category.html'  
    paginate_by = settings.DEFAULT_PAGINATION  # Number of items per page  
    api_url = 'http://127.0.0.1:8000/api/'
    

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)  
        return context


    def get(self, request, *args, **kwargs):
        page_number = request.GET.get('page', 1)
        search_query = request.GET.get('q', '')
        
        category_slug = self.kwargs['slug']        
        category = get_object_or_404(Category, slug=category_slug)
        # user = request.user
        
        api_url = f'{self.api_url}category/{category.slug}/quotes/?page={page_number}&q={search_query}'
        response = requests.get(api_url)

        if response.status_code == 200:
            data = response.json()  
            # print(type(data))
            # print(data)
            count = data.get('count')                   
            quotes = data.get('results', [])
            next_page_url = data.get('next')
            previous_page_url = data.get('previous')                 
        else:
            quotes = []
            next_page_url = None
            
            
        # Replace /api/likes/ with the correct frontend path
        lang = request.LANGUAGE_CODE        
        if next_page_url:
            next_page_url = next_page_url.replace(f'/api/category/{category_slug}/quotes/', f'/{lang}/category/{category_slug}/')

        if previous_page_url:
            previous_page_url = previous_page_url.replace(f'/api/category/{category_slug}/quotes/', f'/{lang}/category/{category_slug}/')            


        category_api_url = f'{self.api_url}category/{category.slug}/'
        response_category = requests.get(category_api_url)

        if response_category.status_code == 200:
            category = response_category.json()
        else:
            category = [] # Raise an error ?

        context = {
            'category': category,
            'quotes': quotes,
            'count': count,                        
            'page_number': page_number,              
            'next_page_url': next_page_url,
            'previous_page_url': previous_page_url,      
            'search_query': search_query,    
        }
        
        # print(context['category'])
        
        # If it's an HTMX request, return only the quotes part
        if request.htmx:
            return render(request, 'quotes_cards.html', context)        

        return render(request, self.template_name, context)
    
  


class HomeView(ListView): # LoginRequiredMixin
    context_object_name = 'quotes'
    template_name = 'home.html'
    paginate_by = settings.DEFAULT_PAGINATION  # Number of items per page 
    api_url = 'http://127.0.0.1:8000/api/'    
    

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)  
        return context


    def get(self, request, *args, **kwargs):
        page_number = request.GET.get('page', 1)
        search_query = request.GET.get('q', '')

        # user = self.request.user
         
        access_token = self.request.session.get('access_token')

        headers = {
            'Authorization': f'Bearer {access_token}',
        }
        
        recommandation_api_url = f'{self.api_url}home/?page={page_number}&q={search_query}'
        
        response = requests.get(recommandation_api_url, headers=headers)
        
        
        # If unauthorized, try to refresh token and retry request
        if response.status_code == 401:
            new_access_token = self.refresh_access_token()
            if new_access_token:
                headers['Authorization'] = f'Bearer {new_access_token}'
                response = requests.get(recommandation_api_url, headers=headers)
            else:
                response = requests.get(recommandation_api_url)

        if response.status_code == 200:
            data = response.json()  
            count = data.get('count')                   
            quotes = data.get('results', [])
            next_page_url = data.get('next')
            previous_page_url = data.get('previous')   
       
        else:
            quotes = []
            count = 0       
            next_page_url = None 


        # Replace /api/likes/ with the correct frontend path
        lang = request.LANGUAGE_CODE        
        if next_page_url:
            next_page_url = next_page_url.replace(f'/api/home/', f'/{lang}/')

        if previous_page_url:
            previous_page_url = previous_page_url.replace(f'/api/home/', f'/{lang}/')

        context = {
            'quotes': quotes,
            'page_number': page_number,    
            'count': count,                      
            'page_number': page_number,              
            'next_page_url': next_page_url,
            'previous_page_url': previous_page_url,         
        }
        
        
        # If it's an HTMX request, return only the quotes part
        if request.htmx:
            return render(request, 'quotes_cards.html', context)        

        return render(request, self.template_name, context)    
    
    
    def refresh_access_token(self):
        refresh_token = self.request.session.get('refresh_token')
        if refresh_token:
            response = requests.post(
                'http://127.0.0.1:8000/api/token/refresh/',
                json={'refresh': refresh_token},
                headers={'Content-Type': 'application/json'},
            )
            if response.status_code == 200:
                data = response.json()
                new_access_token = data.get('access')
                if new_access_token:
                    self.request.session['access_token'] = new_access_token
                    return new_access_token
        return None    

  
  
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