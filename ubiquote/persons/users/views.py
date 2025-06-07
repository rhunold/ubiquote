from django.shortcuts import render, redirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from django.contrib.auth import login
from rest_framework_simplejwt.tokens import RefreshToken
from django.http import JsonResponse

from django.urls import reverse, reverse_lazy
from django.db.models import Max

from django.contrib import messages

from django.views import generic
# from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied

from .forms import UserCreationForm, UserChangeForm, AuthenticationForm

from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView

from texts.quotes.models import Quote, QuotesLikes
from api.mixins import QuotesFetchingMixin, TokenRefreshMixin 


from .models import User
from .forms import  UserForm
from django.conf import settings

# from texts.quotes.views import like_quote

from django.contrib.auth import views as auth_views
from django.utils.translation import get_language
import re

import requests

from django.utils.http import url_has_allowed_host_and_scheme



# @login_required
class GetUserLikesView(LoginRequiredMixin, ListView):
    model = Quote
    context_object_name = 'quotes'  
    template_name = 'get_user_likes.html'
    paginate_by = settings.DEFAULT_PAGINATION  # Number of items per page  
    
    # API URL for quotes list
    api_url = 'http://127.0.0.1:8000/api'        

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


    def get(self, request, *args, **kwargs):
        page_number = request.GET.get('page', 1)
        profil_slug = self.kwargs['slug']
        search_query = request.GET.get('q', '')           
        user = request.user
        
        # Default to computed start_index if not passed from HTMX
        incoming_start_index = request.GET.get('start_index')
        if incoming_start_index is not None:
            start_index = int(incoming_start_index)
        else:
            # Only for first page or full render
            start_index = 0          
                

        # Adjust API URL to pass pagination and search query
        likes_api_url = f'{self.api_url}/likes/{profil_slug}/?page={page_number}'
        # quote_response = requests.get(api_url, headers={'Authorization': f'Token {request.user.auth_token}'})
        
        # quote_api_url = f'http://127.0.0.1:8000/api/user/{profil.slug}/quotes/?page={page_number}'
        response = requests.get(likes_api_url)

        if response.status_code == 200:
            data = response.json()
            # print(data)
            quotes = data.get('results', [])
            count = data.get('count', 0)             
            next_page_url = data.get('next')
            previous_page_url = data.get('previous')            
        else:
            quotes = []
            next_page_url = None
            previous_page_url = None            

        lang = request.LANGUAGE_CODE
        # Replace /api/likes/ with the correct frontend path
        if next_page_url:
            next_page_url = next_page_url.replace('/api/', f'/{lang}/')

        # print(previous_page_url)
        if previous_page_url:
            previous_page_url = previous_page_url.replace('/api/', f'/{lang}/')
        # print(previous_page_url)            

        profil_api_url = f'{self.api_url}/user/{profil_slug}/'
        profil_response = requests.get(profil_api_url)

        if profil_response.status_code == 200:
            profil = profil_response.json()

        else:
            profil = []


        context = {
            'profil': profil, 
            'quotes': quotes,
            'count': count,
            'start_index': start_index,            
            'page_number': page_number,
            'next_page_url': next_page_url,
            'previous_page_url': previous_page_url,
            'search_query': search_query,      
        }    
        
        # If it's an HTMX request, return only the quotes part
        if request.htmx:

            return render(request, 'partials/quotes_cards.html', context)        

        return render(request, self.template_name, context)    



class UserRegisterView(generic.CreateView):
    form_class = UserCreationForm
    template_name = 'registration/register.html'
    # success_url = reverse_lazy('users:login')
    success_url = reverse_lazy('texts:get-home')
    
    
    def form_valid(self, form):
        response = super().form_valid(form)
        user = form.save()
        login(self.request, user)  # Automatically logs the user in
        return redirect(self.success_url) # Redirects to the home page    
    

class LoginView(auth_views.LoginView):
    form_class = AuthenticationForm
    template_name = 'registration/login.html'
    success_url = reverse_lazy('texts:get-home')  # Fallback
    EXCEPTION_PATHS =  [
        r'^(/..)?/register/?$',  # optional 2-letter lang prefix
    ]

    def form_valid(self, form):
        request = self.request
        user = form.get_user()
        login(request, user)

        # JWT tokens
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        refresh_token = str(refresh)

        # Extract "next" from POST or GET
        next_url = request.POST.get('next') or request.GET.get('next')
        
         # Validate and sanitize next_url
        if not next_url:
            next_url = None
        else:
            for pattern in self.EXCEPTION_PATHS:
                if re.match(pattern, next_url):
                    next_url = str(self.success_url)
                    break

        # HTMX support: use HX-Redirect
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            response = JsonResponse({
                'access_token': access_token,
                'refresh_token': refresh_token,
            })
            response['HX-Redirect'] = next_url or str(self.success_url)
            return response

        # Classic POST fallback
        return redirect(next_url or self.success_url)
    
    # def get_context_data(self, **kwargs):
    #     context = super().get_context_data(**kwargs)
    #     context['next_like'] = self.request.GET.get('next_like')
    #     return context      

    # def form_valid(self, form):
    #     # Call the parent form_valid method
    #     response = super().form_valid(form)

    #     # Retrieve the quote ID from the session
    #     quote_id = self.request.GET.get('quote_id')
        
    #     # If the quote ID exists, like the quote and redirect the user
    #     if quote_id:
    #         # Like the quote (add your logic here)
    #         like_quote(self.request, quote_id)
            
    #         # Redirect the user back to the initial page
    #         return redirect(reverse('users:get-user-likes', kwargs={'slug': self.request.user.slug}))
        

    #     return response  # Return the original response if no quote ID is found    
    
class LogoutView(auth_views.LogoutView):
    form_class = AuthenticationForm
    template_name = 'registration/logout.html'
    success_url = reverse_lazy('texts:home')
    
    # def dispatch(self, request, *args, **kwargs):
    #     # Clear the session variable for randomization /// Normalement natif et je devrais pas avoir besoin....
    #     request.session.pop('randomized_homepage', None)
    #     return super().dispatch(request, *args, **kwargs)    


class GetUsersView(ListView):
    model = User
    template_name = 'get_users.html'
    context_object_name = 'users'
    ordering =['username']


    

class GetUserView(QuotesFetchingMixin, ListView):
    template_name = 'get_user.html'
    api_url = settings.API_URL
    

    def get(self, request, *args, **kwargs):
        page_number = request.GET.get('page', 1)
        profil_slug = self.kwargs['slug']
        search_query = request.GET.get('q', '')  
        
        # Default to computed start_index if not passed from HTMX
        incoming_start_index = request.GET.get('start_index')
        if incoming_start_index is not None:
            start_index = int(incoming_start_index)
        else:
            # Only for first page or full render
            start_index = 0            

        profil = User.objects.get(slug=profil_slug)        

        # Fetch quotes of the author
        quotes_data = self.get_api_data(page_number, endpoint=f'user/{profil.slug}/quotes/')
        profil_data = self.get_api_data(page_number=0, endpoint=f'user/{profil.slug}/')


        # Handle pagination for quotes
        quotes = quotes_data.get('results', [])
        next_page_url = quotes_data.get('next')
        previous_page_url = quotes_data.get('previous')
        count = quotes_data.get('count', 0)
        
        
        
        # overide url generation to fit this special case
        lang = request.LANGUAGE_CODE
        if next_page_url:
            next_page_url = next_page_url.replace(f'/api/user/{profil.slug}/quotes/', f'/{lang}/user/{profil.slug}/')
        if previous_page_url:
            previous_page_url = previous_page_url.replace(f'/api/user/{profil.slug}/quotes/', f'/{lang}/user/{profil.slug}/')    

        context = {
            'profil': profil_data,
            'quotes': quotes,
            'count': count,
            'start_index': start_index,             
            'page_number': page_number,
            'next_page_url': next_page_url,
            'previous_page_url': previous_page_url,
            'search_query': search_query,
            
        }
        return self.render_htmx_or_full_quotes(request, context)
    



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

