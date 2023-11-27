from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView

from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.contrib import messages

from django.urls import reverse_lazy, reverse

from .models import Quote, QuotesLikes
from .forms import QuoteForm


@login_required
def like_quote(request, id):
  quote = get_object_or_404(Quote, id=id)
  if quote.likes.filter(id=request.user.id).exists():
    quote.likes.remove(request.user)
  else:
    quote.likes.add(request.user)
  return HttpResponseRedirect(request.META['HTTP_REFERER'])


  
def get_user_quotes_likes(self, context):
  quotes = Quote.published.all()
  
  # Create a dictionary to store the likes status for each quote
  liked_quotes = {}
  
  for quote in quotes:
    liked_quotes[quote.id] = False  # Initialize to False by default

    if quote.likes.filter(id=self.request.user.id).exists(): # Check if user has liked the quote previously
      liked_quotes[quote.id] = True

  context['liked_quotes'] = liked_quotes  
  
  return context

class GetQuotesView(ListView):
  model = Quote
  # queryset = Quote.published.all()
  template_name = 'get_quotes.html'
  context_object_name = 'quotes'
  ordering =['-date_created']
  status = 'published'
  
  def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    
    # Get user likes for every like buton on the page
    get_user_quotes_likes(self, context)

    context['user'] = self.request.user 

    return context 
    


class GetQuoteView(DetailView):
  model = Quote
  template_name = 'get_quote.html'
  context_object_name = 'quote'
  status = 'published'
  
  def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    
    # # Get the author slug from the URL parameter
    # quote_slug = self.kwargs['slug']
    
    # # Get the author object based on the slug
    # quote = Quote.published.get(slug=quote_slug)
    
    # Get user likes for buton status      
    
    get_user_quotes_likes(self, context)
    
 
    return context

  
  
 
class AddQuoteView(CreateView):
  model = Quote
  form_class = QuoteForm
  template_name = 'add_quote.html'
  # fields = '__all__'
  
  def get_success_url(self):
      # Redirect to the detail page of the newly created author
      return reverse_lazy('quotes:get-quote', kwargs={'slug': self.object.slug})  
  
  def form_valid(self, form):
      form.instance.contributor = self.request.user
      return super().form_valid(form)  
  
class UpdateQuoteView(UpdateView):
  model = Quote
  form_class = QuoteForm
  template_name = 'update_quote.html'
  # fields = '__all__'  
  def get_success_url(self):
      # Redirect to the detail page of the newly created author
      return reverse_lazy('quotes:get-quote', kwargs={'slug': self.object.slug})
  
class DeleteQuoteView(DeleteView):
  model = Quote
  # form_class = QuoteForm
  template_name = 'delete_quote.html'
  success_url = reverse_lazy('quotes:get-quotes')
  # fields = '__all__'  
