from django.shortcuts import render
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView

from django.utils.translation import gettext as _
from django.utils.translation import get_language, activate

from django.urls import reverse_lazy

from .models import User, Author, Quote

from .forms import QuoteForm

# from textblob import TextBlob
# это компьютерный портал для гиков.    
# text = "It was a beautiful day ."
# lang = TextBlob(text)
# lang_iso639_1 = lang.detect_language()
# print(lang_iso639_1)


class GetQuotestView(ListView):
  model = Quote
  template_name = 'get_quotes.html'
  ordering =['-date_created']


class GetQuotetView(DetailView):
  model = Quote
  template_name = 'get_quote.html'
  
 
class AddQuoteView(CreateView):
  model = Quote
  form_class = QuoteForm
  template_name = 'add_quote.html'
  # fields = '__all__'
  
class UpdateQuoteView(UpdateView):
  model = Quote
  form_class = QuoteForm
  template_name = 'update_quote.html'
  # fields = '__all__'  
  
class DeleteQuoteView(DeleteView):
  model = Quote
  # form_class = QuoteForm
  template_name = 'delete_quote.html'
  success_url = reverse_lazy('texts:get-quotes')
  # fields = '__all__'  


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