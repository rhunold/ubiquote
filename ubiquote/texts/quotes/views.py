from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from api.mixins import DataFetchingMixin, TokenRefreshMixin

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from django.http import HttpResponseRedirect, Http404

from django.contrib import messages

from django.urls import reverse_lazy, reverse
from django.http import JsonResponse
from django.template.loader import render_to_string

from .models import Quote, QuotesLikes, UserQuoteRecommendation
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
# LANGUAGES = settings.LANGUAGES
from django.utils.translation import get_language


from django.template.loader import render_to_string
from django.http import HttpResponse


# from django.http import JsonResponse
from .services import RecommendationService

from django.contrib.auth import logout


import requests

import logging

from django.core.cache import cache
from django.http import HttpResponse


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
        
        # # 🧠 If request is from HTMX and quote is unliked, just return 204 (quote will disappear)
        # if request.headers.get('HX-Request') == 'true':
        #     return HttpResponse(status=204)        
    else:
        # Like the quote
        QuotesLikes.objects.create(user=user, quote=quote)
        liked = True
        
        # Recommand quotes based on the quote liked
        RecommendationService.recommend_quotes_for_liked_quote(quote=quote, user=user)

    # # Refresh the quote from DB to get updated likes
    # quote.refresh_from_db()
    
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
        search_query = request.GET.get('q', '')
        # lang = request.GET.get('lang', 'en')
        print(search_query)  

        # Fetch data for the home view (e.g., recommendations)
        data = self.get_api_data(
            page_number, 
            endpoint='quotes/', 
            search_query=search_query,
            # extra_params={'lang': lang} 
            )  # Custom endpoint for HomeView

        # Handle pagination and results
        quotes = data.get('results', [])
        next_page_url, previous_page_url = self.process_pagination(data, request)
        count = data.get('count', 0)

        context = {
            'quotes': quotes,  # Keep this as 'quotes' if your template expects it
            'count': count,
            'page_number': page_number,
            'next_page_url': next_page_url,
            'previous_page_url': previous_page_url,
            'search_query' : search_query,
        }
        return self.render_htmx_or_full_quotes(request, context)

        

class GetQuoteView(DetailView):
    model = Quote
    template_name = 'get_quote.html'
    context_object_name = 'quote'
    api_url = settings.API_URL
    
    def get_object(self, queryset=None):
        slug = self.kwargs.get('slug')
        # Extract the ID from the slug (last part after the last hyphen)
        quote_id = slug.split('-')[-1]
        try:
            # return Quote.objects.select_related('author').get(id=quote_id)
            return Quote.objects.get(id=quote_id)
        except Quote.DoesNotExist:
            raise Http404("Quote not found")

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
        
     
        
        # quote = get_object_or_404(Quote, id=quote_id)
        # # Optional: verify author slug matches
        # author_slug = self.kwargs.get('author_slug')
        # if quote.author and quote.author.slug != author_slug:
        #     raise Http404("Author slug mismatch")        
        

        
        # Fetch the quote data from the API using the ID
        data = self.get_api_data(quote_id)  
                     

        # Prepare context with the API data
        context = {
            'quote': data,
            'search_query':None,
        }

        # return render(request, self.template_name, context)
    
        return render(request, self.get_template_names(), context)
    
    def get_template_names(self):
            """Choose the template dynamically based on the URL or other criteria."""
            if '/img/' in self.request.path:
                return ['get_img_quote.html']  # Use another template
            return ['get_quote.html']  # Default template    
  
  

class AddQuoteView(LoginRequiredMixin, DataFetchingMixin, CreateView):
    model = Quote
    form_class = QuoteForm
    template_name = 'add_quote.html'
    api_url = settings.API_URL
  
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_success_url(self):
        return reverse_lazy('quotes:get-quote', kwargs={'slug': self.object.slug})  
        
        
    def form_valid(self, form):
        author = form.cleaned_data.get('author')
        categories = form.cleaned_data.get('categories')

        data = {
            'text': form.cleaned_data['text'],
            'lang': form.cleaned_data['lang'],
            'author_id': author.id if author else None,  # matches serializer field
            'category_ids': [cat.id for cat in categories] if categories else []  # matches serializer field
        }

        # print(data)
        

        # API request
        response = self.create_api_data('quote/create/', data)

        if isinstance(response, dict) and 'id' in response:
            try:
                self.object = Quote.objects.get(id=response['id'])
                return HttpResponseRedirect(self.get_success_url())
            except Quote.DoesNotExist:
                form.add_error(None, "Quote created via API but not found locally.")
                return self.form_invalid(form)

        # Handle errors (e.g., duplicate)
        if isinstance(response, dict) and 'non_field_errors' in response:
            for error in response['non_field_errors']:
                form.add_error(None, error)
            return self.form_invalid(form)

        # Fallback error
        form.add_error(None, "Failed to create quote : duplicate content, too short or too long. Please try again.")
        return self.form_invalid(form)
        
        
        # # Create quote through API
        # response_data = self.create_api_data('quote/create/', data)

        # if response_data and 'id' in response_data:
        #     try:
        #         self.object = Quote.objects.get(id=response_data['id'])
        #         return HttpResponseRedirect(self.get_success_url())
        #     except Quote.DoesNotExist:
        #         messages.error(self.request, "Quote created but not found locally.")
        #         return self.form_invalid(form)

        # messages.error(self.request, "Failed to create quote. Please try again.")
        # return self.form_invalid(form)
    
    
    
    # def form_valid(self, form):
    #     # Prepare data for API
    #     data = {
    #         'text': form.cleaned_data['text'],
    #         'author_id': form.cleaned_data['author'].id,
    #         'lang': form.cleaned_data['lang'],
    #         'category_ids': [cat.id for cat in form.cleaned_data['categories']]
    #     }
        
    #     # Create quote through API
    #     response_data = self.create_api_data('quote/create/', data)
        
    #     if response_data:
    #         # Set the object for get_success_url
    #         self.object = Quote.objects.get(id=response_data['id'])
    #         return HttpResponseRedirect(self.get_success_url())
        
    #     # If API call failed, show error
    #     messages.error(self.request, "Failed to create quote. Please try again.")
    #     return self.form_invalid(form)
 
# @login_required   
class UpdateQuoteView(LoginRequiredMixin, DataFetchingMixin, UpdateView):
    model = Quote
    form_class = QuoteForm
    template_name = 'update_quote.html'
    api_url = settings.API_URL
    
    def get_success_url(self):
        return reverse_lazy('quotes:get-quote', kwargs={'slug': self.object.slug})
    
    def form_valid(self, form):
        # Prepare data for API
        data = {
            'text': form.cleaned_data['text'],
            'author_id': form.cleaned_data['author'].id,
            'lang': form.cleaned_data['lang'],
            'dimensions': form.cleaned_data['dimensions'],
            'category_ids': [cat.id for cat in form.cleaned_data['categories']]
        }
        
        # print(data)
        
        # Update quote through API
        quote_id = self.object.id
        response_data = self.update_api_data(f'quote/{quote_id}/update/', data, method='patch')
        
        if response_data:
            # Refresh the object from database
            self.object.refresh_from_db()
            return HttpResponseRedirect(self.get_success_url())
        
        # If API call failed, show error
        messages.error(self.request, "Failed to update quote. Please try again.")
        return self.form_invalid(form)

class DeleteQuoteView(LoginRequiredMixin, DataFetchingMixin, DeleteView):
    model = Quote
    template_name = 'delete_quote.html'
    success_url = reverse_lazy('quotes:get-quotes')
    api_url = settings.API_URL

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        success_url = self.get_success_url()
        
        # Delete through API
        if self.delete_api_data(f'quote/{self.object.id}/delete/'):
            return HttpResponseRedirect(success_url)
        
        # If API call failed, show error
        messages.error(self.request, "Failed to delete quote. Please try again.")
        return self.render_to_response(self.get_context_data())
    
    
    # def get_object(self, queryset=None):
    #     try:
    #         return Quote.objects.get(slug=self.kwargs['slug'])
    #     except Quote.DoesNotExist:
    #         raise Http404("Quote not found")    
    
    # @method_decorator(login_required)
    # def dispatch(self, *args, **kwargs):
    #     return super().dispatch(*args, **kwargs)
    

# class GetAuthorQuotesView(ListView):
#     model = Quote
#     template_name = 'author_quotes.html'
#     context_object_name = 'quotes'
#     paginate_by = 10
    
#     def get_queryset(self):
#         author_slug = self.kwargs.get('slug')
#         return Quote.objects.filter(author__slug=author_slug).order_by('-date_created')
    
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         author_slug = self.kwargs.get('slug')
#         context['author'] = get_object_or_404(Author, slug=author_slug)
#         return context
    
