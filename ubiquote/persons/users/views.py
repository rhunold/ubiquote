from django.shortcuts import render

from django.views import generic
# from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required

from .forms import UserCreationForm, UserChangeForm, AuthenticationForm

from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView

from texts.quotes.models import Quote, QuotesLikes


from .models import User
from .forms import  UserForm
from django.conf import settings

from django.contrib.auth import views as auth_views
from django.utils.translation import get_language


from django.urls import reverse_lazy


class GetUserLikesView(ListView):
  model = Quote
  context_object_name = 'quotes'  
  template_name = 'get_user_likes.html'
  paginate_by = settings.DEFAULT_PAGINATION  # Number of items per page  
  
  def get_context_data(self, **kwargs):
      context = super().get_context_data(**kwargs)
      
      # # Get the profil slug from the URL parameter
      profil_slug = self.kwargs['slug']
      
      # # Get the profil object based on the slug
      profil = User.objects.get(slug=profil_slug)       
      
      context['profil'] = profil

      quotes = context['quotes']  # Get the queryset of quotes
      quotes_like_statut = {quote.id: QuotesLikes.has_user_liked(profil, quote) for quote in quotes}
      liked_quotes = [quote_id for quote_id, liked in quotes_like_statut.items() if liked]  
      context['liked_quotes'] = liked_quotes      
                  
      # Get total number of quotes in the database
      total_quotes = Quote.published.filter(likes=profil).count()
      context['total_quotes'] = total_quotes   
      
      
      user_language = get_language()   
    
      translated_names = {}
      for quote in quotes:
          author = quote.author
          if author:
              translated_names[quote.id] = author.get_translation(user_language)
              print("1")
          else:
              translated_names[quote.id] = 'Unknown'
              print('2')
      
      context['translated_names'] = translated_names         
      
      return context
    

  def get_queryset(self):
      user = self.request.user
      liked_quote_ids = QuotesLikes.objects.filter(user=user).values_list('quote_id', flat=True)
      return Quote.objects.filter(id__in=liked_quote_ids).select_related('author').order_by('-date_created')

  

class UserRegisterView(generic.CreateView):
    form_class = UserCreationForm
    template_name = 'registration/register.html'
    success_url = reverse_lazy('users:login')
    
    
class LoginView(auth_views.LoginView):
    form_class = AuthenticationForm
    template_name = 'registration/login.html'
    success_url = reverse_lazy('texts:home')
    # def get_success_url(self):
    #     # Redirect to the detail page of the newly created author
    #     return reverse_lazy('users:get-user', kwargs={'slug': self.object.slug})    
    
class LogoutView(auth_views.LogoutView):
    form_class = AuthenticationForm
    template_name = 'registration/logout.html'
    success_url = reverse_lazy('texts:home')


class GetUsersView(ListView):
  model = User
  template_name = 'get_users.html'
  context_object_name = 'users'
  ordering =['username']


class GetUserView(ListView):
  model = Quote 
  context_object_name = 'quotes'  
  template_name = 'get_user.html'
  paginate_by = settings.DEFAULT_PAGINATION    
  
  def get_context_data(self, **kwargs):
      context = super().get_context_data(**kwargs)
      
      # Get the author object based on the slug
      profil = User.objects.get(slug=self.kwargs['slug'])
      context['profil'] = profil  # Pass the category object to the template
      # context['title'] = category.title   
      
      # user = self.request.user
      quotes = context['quotes']  # Get the queryset of quotes
      quotes_like_statut = {quote.id: QuotesLikes.has_user_liked(profil, quote) for quote in quotes}
      liked_quotes = [quote_id for quote_id, liked in quotes_like_statut.items() if liked]  
      context['liked_quotes'] = liked_quotes      
                  
      # Get total number of quotes in the database
      total_quotes = Quote.published.filter(contributor__slug=profil) .count()
      context['total_quotes'] = total_quotes
      
      user_language = get_language()   
    
      translated_names = {}
      for quote in quotes:
          author = quote.author
          if author:
              translated_names[quote.id] = author.get_translation(user_language)
              print("1")
          else:
              translated_names[quote.id] = 'Unknown'
              print('2')
      
      context['translated_names'] = translated_names       
         
      return context

  def get_queryset(self):
      # Get the profil slug
      user_slug = self.kwargs['slug']
      
      # Filter quotes by the contributor slug
      queryset = Quote.published.filter(contributor__slug=user_slug).order_by("-date_created")
      
      return queryset


class AddUserView(CreateView):
  model = User
  form_class = UserForm
  template_name = 'add_user.html'
  def get_success_url(self):
      # Redirect to the detail page of the newly created user
      return reverse_lazy('users:get-user', kwargs={'slug': self.object.slug})
  # fields = '__all__'
  

  
class UpdateUserView(UpdateView):
  model = User
  form_class = UserForm
  template_name = 'update_user.html'
  # fields = '__all__'  
  def get_success_url(self):
      # Redirect to the detail page of the newly updated user
      return reverse_lazy('users:get-user', kwargs={'slug': self.object.slug})
  
  
class DeleteUserView(DeleteView):
  model = User
  # form_class = QuoteForm
  template_name = 'delete_user.html'
  success_url = reverse_lazy('users:get-users')
  # fields = '__all__'  

