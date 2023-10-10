from django.shortcuts import render
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView

# from django.utils.translation import gettext as _
# from django.utils.translation import get_language, activate

from django.urls import reverse_lazy

from .models import Quote
from .forms import QuoteForm



class GetQuotesView(ListView):
  model = Quote
  template_name = 'get_quotes.html'
  context_object_name = 'quotes'
  ordering =['-date_created']


class GetQuoteView(DetailView):
  model = Quote
  template_name = 'get_quote.html'
  
 
class AddQuoteView(CreateView):
  model = Quote
  form_class = QuoteForm
  template_name = 'add_quote.html'
  # fields = '__all__'
  
  def form_valid(self, form):
      form.instance.contributor = self.request.user
      return super().form_valid(form)  
  
class UpdateQuoteView(UpdateView):
  model = Quote
  form_class = QuoteForm
  template_name = 'update_quote.html'
  # fields = '__all__'  
  
class DeleteQuoteView(DeleteView):
  model = Quote
  # form_class = QuoteForm
  template_name = 'delete_quote.html'
  success_url = reverse_lazy('quotes:get-quotes')
  # fields = '__all__'  
