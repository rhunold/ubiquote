from django.shortcuts import render

from django.utils.translation import gettext as _
from django.utils.translation import get_language, activate

from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404

from .models import Category
from texts.quotes.models import Quote
# from texts.quotes.views import get_user_quotes_likes
from django.views.generic import ListView, DetailView  # CreateView, UpdateView, DeleteView


class GetCategoriesView(ListView):
  model = Category
  template_name = 'get_categories.html'
  context_object_name = 'categories'  
  # ordering =['-date_created']


class GetCategoryView(ListView):
  model = Quote
  queryset = Quote.published.all()  
  context_object_name = 'quotes'
  template_name = 'get_category.html'
  
  def get_context_data(self, **kwargs):
      context = super().get_context_data(**kwargs)
      
      # Get user likes for buton status           
      
      # Get the category id from the URL parameter
      category_slug = self.kwargs['slug']
      
      # Get the category object based on the id
      category = Category.objects.get(slug=category_slug)
      
      context['category'] = category  # Pass the category object to the template
    
      return context  
  
  def get_queryset(self):
      # Get the category id from the URL parameter
      category_slug = self.kwargs['slug']    
      
      # Filter quotes by the category id
      queryset = Quote.published.filter(categories__slug=category_slug)
      
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