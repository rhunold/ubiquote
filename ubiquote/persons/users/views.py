from django.shortcuts import render

from django.views import generic
# from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required

from .forms import UserCreationForm, UserChangeForm, AuthenticationForm

from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView

from texts.quotes.models import Quote
from texts.quotes.views import get_user_quotes_likes

from .models import User
from .forms import  UserForm

from django.contrib.auth import views as auth_views

from django.urls import reverse_lazy

@login_required
def user_likes(request):
  # Get user likes for buton status
  quotes = Quote.published.filter(likes=request.user)
  return render(request, 'users:get_user_likes', {'quotes': quotes})


class GetUserLikesView(ListView):
  model = Quote
  queryset = Quote.published.all()
  
  context_object_name = 'quotes'  
  template_name = 'get_user_likes.html'
  
  def get_context_data(self, **kwargs):
      context = super().get_context_data(**kwargs)
      
      # Get user likes for buton status
      get_user_quotes_likes(self, context)       
      
      # Get the profil slug from the URL parameter
      profil_slug = self.kwargs['slug']
      
      # Get the profil object based on the slug
      profil = User.objects.get(slug=profil_slug)
      
      quotes = Quote.published.filter(likes=profil.id)
      context['quotes'] = quotes           
      
      context['profil'] = profil
      return context

  def get_queryset(self):
      # Get the profil id from the URL parameter
      profil_slug = self.kwargs['slug']   
      profil = User.objects.get(slug=profil_slug)
      
      # Filter quotes by the profil id
      queryset = Quote.published.filter(likes=profil.id) 
      
      return queryset
  

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
  # model = Author
  model = Quote
  queryset = Quote.published.all()  
  context_object_name = 'quotes'  
  template_name = 'get_user.html'
  
  def get_context_data(self, **kwargs):
      context = super().get_context_data(**kwargs)
      
      # Get user likes for buton status
      get_user_quotes_likes(self, context)
      
      # Get the author object based on the slug
      profil = User.objects.get(slug=self.kwargs['slug'])
      
      context['profil'] = profil  # Pass the category object to the template
      # context['title'] = category.title      
      return context

  def get_queryset(self):
      # Get the category id from the URL parameter
      user_slug = self.kwargs['slug']
      
      # Filter quotes by the category id
      queryset = Quote.published.filter(contributor__slug=user_slug) 
      
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

