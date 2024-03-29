from django.shortcuts import render

from django.utils.translation import gettext as _
from django.utils.translation import get_language, activate

from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404

from .models import Category
from texts.quotes.models import Quote
from texts.quotes.views import LanguageFilterMixin
# from texts.quotes.views import get_user_quotes_likes
from django.views.generic import ListView, DetailView  # CreateView, UpdateView, DeleteView

from django.conf import settings
LANGUAGES = settings.LANGUAGES


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



def home(request):
    trans = translate(language='fr')
    return render(request, 'home.html', {'trans' : trans})

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