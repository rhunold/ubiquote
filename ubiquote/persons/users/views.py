from django.shortcuts import render

from django.views import generic
# from django.contrib.auth.forms import UserCreationForm

from .forms import UserCreationForm, UserChangeForm, AuthenticationForm

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

