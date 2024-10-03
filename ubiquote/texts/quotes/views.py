from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from texts.mixins import DataFetchingMixin, TokenRefreshMixin

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from django.http import HttpResponseRedirect, Http404

from django.contrib import messages

from django.urls import reverse_lazy, reverse
from django.http import JsonResponse
from django.template.loader import render_to_string

from .models import Quote, QuotesLikes
from .forms import QuoteForm

from django.db.models import Q

from persons.authors.models import Author

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Count, Prefetch
from django.core.cache import cache
from django.contrib.auth import get_user_model
from django.conf import settings

from django.http import JsonResponse
from django.contrib.postgres.search import SearchVector

from django.shortcuts import render
# from elasticsearch import Elasticsearch

from django.conf import settings
LANGUAGES = settings.LANGUAGES
from django.utils.translation import get_language


from django.template.loader import render_to_string
from django.http import HttpResponse


# from django.http import JsonResponse
from .services import RecommendationService

from django.contrib.auth import logout


import requests

import logging

from django.core.cache import cache



# Set up logger for error handling
logger = logging.getLogger(__name__)

    
@login_required
def like_quote(request, id):
    quote = get_object_or_404(Quote, id=id)
    user = request.user
    liked = QuotesLikes.objects.filter(user=user, quote=quote).exists()
    
    if liked:
        # Unlike the quote
        QuotesLikes.objects.filter(user=user, quote=quote).delete()
        liked = False
    else:
        # Like the quote
        QuotesLikes.objects.create(user=user, quote=quote)
        liked = True
        

    # Render the updated like area using the partial template
    context = {
        'quote': quote,
        'liked': liked,
    }
    
    return render(request, 'like_quote.html', context)          

        

# def recommend_quotes(request, user_id):
#     recommended_quotes = RecommendationService.recommend_quotes(user_id)
#     return render(request, 'recommended_quotes.html', {'recommended_quotes': recommended_quotes})





class GetQuotesView(DataFetchingMixin, ListView):
    template_name = 'get_quotes.html'
    api_url = settings.API_URL
    

    def get(self, request, *args, **kwargs):
        page_number = request.GET.get('page', 1)

        # Fetch data for the home view (e.g., recommendations)
        data = self.get_api_data(page_number, endpoint='quotes/')  # Custom endpoint for HomeView

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

        

class GetQuoteView(DetailView):
    template_name = 'get_quote.html'
    # context_object_name = 'quote'
    api_url = settings.API_URL
    

    def get_api_data(self, quote_id):
        """Fetch individual quote data from the API with error handling."""
        api_url = f'{self.api_url}quote/{quote_id}/'
        try:
            response = requests.get(api_url)
            response.raise_for_status()  # Raise error if response status code is not 200
            return response.json()
        except requests.exceptions.RequestException as e:
            # Log the error and handle the failure case
            return {'error': str(e)}

    def get(self, request, *args, **kwargs):
        """Fetch quote by slug, then use the API to get quote details."""
        slug = self.kwargs.get('slug')
        
        # Fetch quote from the local DB to get the ID
        quote = get_object_or_404(Quote, slug=slug)
        quote_id = quote.id  # Get the ID of the quote
    
        
        # Fetch the quote data from the API using the ID
        data = self.get_api_data(quote_id)       

        # Prepare context with the API data
        context = {
            'quote': data,
        }

        return render(request, self.template_name, context)
  
  

class AddQuoteView(LoginRequiredMixin, CreateView):
    model = Quote
    form_class = QuoteForm
    template_name = 'add_quote.html'
    # fields = '__all__'
  
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_success_url(self):
        return reverse_lazy('quotes:get-quote', kwargs={'slug': self.object.slug})  
    
    def form_valid(self, form):
        form.instance.contributor = self.request.user
        return super().form_valid(form) 
 
# @login_required   
class UpdateQuoteView(LoginRequiredMixin, UpdateView):
    model = Quote
    form_class = QuoteForm
    template_name = 'update_quote.html'
    
    # @method_decorator(login_required)
    # def dispatch(self, *args, **kwargs):
    #     return super().dispatch(*args, **kwargs)
    
    # fields = '__all__'  
    def get_success_url(self):
        # Redirect to the detail page of the newly created author
        return reverse_lazy('quotes:get-quote', kwargs={'slug': self.object.slug})

# @method_decorator(login_required, name='dispatch')
class DeleteQuoteView(LoginRequiredMixin, DeleteView):
    model = Quote
    # form_class = QuoteForm
    template_name = 'delete_quote.html'
    success_url = reverse_lazy('quotes:get-quotes')
    # fields = '__all__' 
    
    
    # def get_object(self, queryset=None):
    #     try:
    #         return Quote.objects.get(slug=self.kwargs['slug'])
    #     except Quote.DoesNotExist:
    #         raise Http404("Quote not found")    
    
    # @method_decorator(login_required)
    # def dispatch(self, *args, **kwargs):
    #     return super().dispatch(*args, **kwargs)
    
