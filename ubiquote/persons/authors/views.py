from django.shortcuts import render
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView

from django.urls import reverse_lazy

from .models import Author
from texts.quotes.models import Quote
# from .forms import QuoteForm



class GetAuthorsView(ListView):
  model = Author
  template_name = 'get_authors.html'
  context_object_name = 'authors'
  ordering =['last_name']


class GetAuthorView(ListView):
  # model = Author
  model = Quote
  context_object_name = 'quotes'  
  template_name = 'get_author.html'
  
  def get_context_data(self, **kwargs):
      context = super().get_context_data(**kwargs)
      # Get the author slug from the URL parameter
      author_slug = self.kwargs['slug']
      
      # Get the author object based on the slug
      author = Author.objects.get(slug=author_slug)
      
      context['author'] = author  # Pass the category object to the template
      # context['title'] = category.title      
      return context

  def get_queryset(self):
      # Get the category id from the URL parameter
      author_slug = self.kwargs['slug']
      
      # Filter quotes by the category id
      queryset = Quote.objects.filter(author__slug=author_slug) 
      
      return queryset
  
 
# class AddAuthorView(CreateView):
#   model = Author
#   form_class = AuthorForm
#   template_name = 'add_author.html'
#   # fields = '__all__'
  

  
# class UpdateAuthorView(UpdateView):
#   model = Author
#   form_class = AuthorForm
#   template_name = 'update_author.html'
#   # fields = '__all__'  
  
class DeleteAuthorView(DeleteView):
  model = Author
  # form_class = QuoteForm
  template_name = 'delete_author.html'
  success_url = reverse_lazy('author:get-authors')
  # fields = '__all__'  
