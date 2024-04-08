import random
from django.shortcuts import render

from django.utils.translation import gettext as _
from django.utils.translation import get_language, activate
from django.contrib.auth.decorators import login_required

from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404

from .models import Category
from texts.quotes.models import Quote
from texts.quotes.views import LanguageFilterMixin
# from texts.quotes.views import get_user_quotes_likes
from django.views.generic import ListView, DetailView  # CreateView, UpdateView, DeleteView

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from django.conf import settings
LANGUAGES = settings.LANGUAGES

from texts.quotes.services import RecommendationService


class GetCategoriesView(ListView):
  model = Category
  template_name = 'get_categories.html'
  context_object_name = 'categories'  
  # ordering =['-date_created']


class GetCategoryView(LanguageFilterMixin, ListView):
  model = Quote
  queryset = Quote.published.all()  
  context_object_name = 'quotes'
  template_name = 'get_category.html'
  ordering =['-date_created'] 
  paginate_by = settings.DEFAULT_PAGINATION  # Number of items per page  
  
  def get_context_data(self, **kwargs):
      context = super().get_context_data(**kwargs)
      
      # Get user likes for buton status           
      
      # Get the category id from the URL parameter
      category_slug = self.kwargs['slug']
      
      # Get the category object based on the id
      category = Category.objects.get(slug=category_slug)
      
      context['category'] = category  # Pass the category object to the template
      
      # Get translated names for authors
      if hasattr(self, 'request'):
          language_code = self.request.LANGUAGE_CODE
      else:
          language_code = 'en'  # Default language if language code is not available
      
      translated_names = {}
      
      
      quotes = context['quotes']  # Get the queryset of quotes      
      for quote in quotes:
          author = quote.author
          if author:
              translated_names[quote.id] = author.get_translation(language_code)
          else:
              translated_names[quote.id] = 'Unknown'
      
      context['translated_names'] = translated_names      
      
      
      return context  
  
  def get_queryset(self):
      # Get the category id from the URL parameter
      category_slug = self.kwargs['slug']    
      
      # Filter quotes by the category id
      queryset = Quote.published.filter(categories__slug=self.kwargs['slug']  )
      
      return queryset



@login_required
def home(request):
  
    recommended_quotes = RecommendationService.recommend_quotes(request.user)
    
    # # Order the recommended quotes by their primary key (id) to provide a consistent order
    quotes = list(recommended_quotes.order_by('date_created'))
    
    
    if hasattr(request, 'LANGUAGE_CODE'):
        language_code = request.LANGUAGE_CODE
    else:
        language_code = 'en'  # Default language if language code is not available
    
        
    translated_names = {}
    for quote in quotes:
        author = quote.author
        if author:
            translated_names[quote.id] = author.get_translation(language_code)
        else:
            translated_names[quote.id] = 'Unknown'    
    
    # context['translated_names'] = translated_names
    
    # Shuffle the list of recommended quotes
    # random.shuffle(quotes)    

    # Paginate the recommended quotes
    page_number = request.GET.get('page', 1)
    paginator = Paginator(quotes, 10)  # Change 10 to the desired number of quotes per page

    try:
        page_obj = paginator.page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    # Pass pagination variables to the template
    context = {
        'translated_names': translated_names,
        'quotes': page_obj,
        # 'quotes': recommended_quotes,
        'page_obj' : page_obj,
        'paginator': paginator,
        'is_paginated': page_obj.has_other_pages(),
    }

    return render(request, 'recommended_quotes.html', context)
  
  
def translate(language):
  cur_language = get_language()
  try:
    activate(language)
    text = _('hello')
  finally:
    activate(cur_language)
  return text
  

# # https://stackoverflow.com/a/66271685
# def get_nationality():
#   nat = Author.objects.get(id=1)
#   return _(nat.nationality)