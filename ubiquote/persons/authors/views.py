from django.shortcuts import render
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView

from django.urls import reverse_lazy

from .models import Author
from .forms import AuthorForm
from texts.quotes.models import Quote
from texts.quotes.views import get_user_likes

# from .forms import QuoteForm


# def get_user_likes(self, context):

#   # EN FAIRE UNE FONCTION CAR DRY / QUOTES ET AUTRES MODELES
#   quotes = Quote.published.all()
#   quotes_count = Quote.published.count()          
  
#   # Create a dictionary to store the likes status for each quote
#   liked_quotes = {}
  
#   for quote in self.queryset:
#     liked_quotes[quote.id] = False  # Initialize to False by default

#     if quote.likes.filter(id=self.request.user.id).exists():
#       liked_quotes[quote.id] = True

#       print(liked_quotes)

#   context['quotes'] = quotes
#   context['quotes_count'] = quotes_count
#   context['liked_quotes'] = liked_quotes  
  
  
#   return context


class GetAuthorsView(ListView):
  model = Author
  template_name = 'get_authors.html'
  context_object_name = 'authors'
  ordering =['last_name']


class GetAuthorView(ListView):
  # model = Author
  model = Quote
  queryset = Quote.published.all()
  context_object_name = 'quotes'  
  template_name = 'get_author.html'
  
  def get_context_data(self, **kwargs):
      context = super().get_context_data(**kwargs)
      
      # Get user likes for buton status
      get_user_likes(self, context)      
      
      # Get the author slug from the URL parameter to Get the author object 
      author_slug = self.kwargs['slug']
      author = Author.objects.get(slug=author_slug)
      context['author'] = author
 
      return context

  def get_queryset(self):
      # Get the category id from the URL parameter
      author_slug = self.kwargs['slug']
      
      # Filter quotes by the manager and same author slug
      queryset = Quote.published.filter(author__slug=author_slug) 
      
      return queryset
    
    

  # def get_context_data(self, **kwargs):
  #   context = super().get_context_data(**kwargs)
  #   quotes = Quote.published.all()
  #   quotes_count = Quote.published.count()    

  #   # Create a dictionary to store the likes status for each quote
  #   liked_quotes = {}
    
  #   for quote in self.queryset:
  #     liked_quotes[quote.id] = False  # Initialize to False by default


  #     if quote.likes.filter(id=self.request.user.id).exists():
  #       liked_quotes[quote.id] = True

  #       print(liked_quotes)

  #   context['quotes'] = quotes
  #   context['quotes_count'] = quotes_count
  #   context['liked_quotes'] = liked_quotes  # Pass the like status dictionary to the template
    
    
  
 
class AddAuthorView(CreateView):
  model = Author
  form_class = AuthorForm
  template_name = 'add_author.html'
  def get_success_url(self):
      # Redirect to the detail page of the newly created author
      return reverse_lazy('authors:get-author', kwargs={'slug': self.object.slug})
  # fields = '__all__'
  

  
class UpdateAuthorView(UpdateView):
  model = Author
  form_class = AuthorForm
  template_name = 'update_author.html'
  # fields = '__all__'  
  def get_success_url(self):
      # Redirect to the detail page of the newly created author
      return reverse_lazy('authors:get-author', kwargs={'slug': self.object.slug})
  
class DeleteAuthorView(DeleteView):
  model = Author
  # form_class = QuoteForm
  template_name = 'delete_author.html'
  success_url = reverse_lazy('author:get-authors')
  # fields = '__all__'  
