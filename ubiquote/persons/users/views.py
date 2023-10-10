from django.shortcuts import render

from django.views import generic
# from django.contrib.auth.forms import UserCreationForm

from .forms import UserCreationForm, UserChangeForm, AuthenticationForm

from django.views.generic import ListView, DetailView

from texts.quotes.models import Quote
from .models import User

from django.contrib.auth import views as auth_views

from django.urls import reverse_lazy

class UserRegisterView(generic.CreateView):
    form_class = UserCreationForm
    template_name = 'registration/register.html'
    success_url = reverse_lazy('users:login')
    
    
class LoginView(auth_views.LoginView):
    form_class = AuthenticationForm
    template_name = 'registration/login.html'
    success_url = reverse_lazy('texts:home')
    
class LogoutView(auth_views.LoginView):
    form_class = AuthenticationForm
    template_name = 'registration/login.html'
    success_url = reverse_lazy('texts:home')


class GetUsersView(ListView):
  model = User
  template_name = 'get_users.html'
  context_object_name = 'users'
  ordering =['username']


class GetUserView(ListView):
  # model = Author
  model = Quote
  context_object_name = 'quotes'  
  template_name = 'get_user.html'
  
  def get_context_data(self, **kwargs):
      context = super().get_context_data(**kwargs)
      # Get the author slug from the URL parameter
      user_slug = self.kwargs['slug']
      
      # Get the author object based on the slug
      user = User.objects.get(slug=user_slug)
      
      context['user'] = user  # Pass the category object to the template
      # context['title'] = category.title      
      return context

  def get_queryset(self):
      # Get the category id from the URL parameter
      user_slug = self.kwargs['slug']
      
      # Filter quotes by the category id
      queryset = Quote.objects.filter(contributor__slug=user_slug) 
      
      return queryset
  
