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
from texts.quotes.models import Quote, QuotesLikes, UserQuoteRecommendation

from django.views.generic import ListView, DetailView  # CreateView, UpdateView, DeleteView
from texts.mixins import DataFetchingMixin, TokenRefreshMixin 

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from django.conf import settings
LANGUAGES = settings.LANGUAGES
from django.utils.translation import get_language

import requests

from rest_framework.permissions import AllowAny


from django.db.models import F

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
            # count = data.get('count', 0)            
            next_page_url = data.get('next')
            
        else:
            categories = []
            count = 0            
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
        search_query = request.GET.get('q', '')         

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
            'search_query': search_query,
            
        }
        return self.render_htmx_or_full_quotes(request, context)



class HomeView(DataFetchingMixin, ListView):
    template_name = 'home.html'
    api_url = settings.API_URL
    
    

    def get(self, request, *args, **kwargs):
        page_number = request.GET.get('page', 1)
        search_query = request.GET.get('q', '')
        user = request.user
        
        # # Fetch data for the home view (e.g., recommendations) and disable cache if randomization is required
        # session = request.session
        # disable_cache = False

        # if not session.get('randomized_homepage', False):
        #     disable_cache = True        
        
        # disable_cache = not request.session.get('randomized_homepage', False)        

        # Fetch data for the home view (e.g., recommendations)
        data = self.get_api_data(page_number, endpoint='', disable_cache=True)  # Custom endpoint for HomeView

        # Handle pagination and results
        results = data.get('results', [])
        next_page_url, previous_page_url = self.process_pagination(data, request)
        count = data.get('count', 0)
        
        
        # # Fetch recommendations for the user
        # recommendations = UserQuoteRecommendation.objects.filter(user=user)

        # # Update show_count for each recommendation
        # recommendations.update(show_count=F('show_count') + 1)

        # # Remove any recommendations that have been shown more than 3 times
        # UserQuoteRecommendation.objects.filter(user=user, show_count__gt=3).delete()

        # # Get the remaining recommendations to display
        # results = [rec.quote for rec in recommendations]   
        
        
        # Randomize if new session
        # if not request.session.get('randomized_homepage', False):
        #     # results = list(results)
        #     random.shuffle(results)
        #     request.session['randomized_homepage'] = True
        #     request.session.save()
             
        

        # # Randomize the results for each new session
        # session = request.session
        # if not session.get('randomized_homepage', False):
        #     random.shuffle(results)  # Randomize quotes
        #     session['randomized_homepage'] = True  # Mark session as randomized
        

        
        # # Randomize the results for each new session
        # if disable_cache:
        #     random.shuffle(results)
        #     session['randomized_homepage'] = True  # Mark session as randomized
        
        
        # print(results.first())     
                 
        
        # # Randomize for new session
        # if not request.session.get('randomized_homepage', False):
        #     # Shuffle the results list
        #     results = list(results) 
        #     results = random.shuffle(results)
        #     # print(type(results))
        #     request.session['randomized_homepage'] = True  # Mark session as randomized
        #     request.session.save()  # Ensure session is saved
        #     print("randomized_homepage")
        
        # # print(results[:10])
        
        # print(type(results))
        # # print(results[0])    

        context = {
            'quotes': results,  # Keep this as 'quotes' if your template expects it
            'count': count,
            'page_number': page_number,
            'next_page_url': next_page_url,
            'previous_page_url': previous_page_url,
            'search_query' : search_query,
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