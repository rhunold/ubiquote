from django.shortcuts import render, redirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

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


from .models import User
from .forms import  UserForm
from django.conf import settings

from texts.quotes.views import like_quote

from django.contrib.auth import views as auth_views
from django.utils.translation import get_language




# @login_required
class GetUserLikesView(LoginRequiredMixin, ListView):
    model = Quote
    context_object_name = 'quotes'  
    template_name = 'get_user_likes.html'
    paginate_by = settings.DEFAULT_PAGINATION  # Number of items per page  
    # login_url = reverse_lazy('login')  # URL name of your login page    
    
    # def get(self, request, *args, **kwargs):
    #     return super().get(request, *args, **kwargs)    
  
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get the profil slug from the URL parameter
        profil_slug = self.kwargs['slug']
        
        context['profil_slug'] = profil_slug        
        # Get the profil object based on the slug
        profil = User.objects.get(slug=profil_slug)       
        context['profil'] = profil
        
        # user = self.request.user      

        quotes = context['quotes']  # Get the queryset of quotes
        
        # Have a track of liked quote to display like button
        quotes_like_statut = {quote.id: QuotesLikes.has_user_liked(profil, quote) for quote in quotes}
        liked_quotes = [quote_id for quote_id, liked in quotes_like_statut.items() if liked]  
        context['liked_quotes'] = liked_quotes
        
        # get the timestamp of when the quoteslikes had been created
        liked_quotes_timestamps = QuotesLikes.objects.filter(user=profil).values('quote_id', 'timestamp')
        context['liked_quotes_timestamps'] = liked_quotes_timestamps


        # Get total number of quotes in the database
        total_quotes = Quote.published.filter(likes=profil).count()
        context['total_quotes'] = total_quotes   
        
        user_language = get_language()   
        
        translated_names = {}
        for quote in quotes:
            author = quote.author
            if author:
                translated_names[quote.id] = author.get_translation(user_language)
                #   print("1")
            #   else:
            #       translated_names[quote.id] = 'Unknown'
            #     #   print('2')
        
        context['translated_names'] = translated_names         
        
        paginator = Paginator(self.get_queryset(), self.paginate_by)
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        context['page_obj'] = page_obj
        context['paginator'] = paginator
        
    
        # if page_obj.has_next():
        #     user_slug = profil.slug # Assuming you're passing the profil in the class
        #     print(user_slug)
        #     next_page_url = reverse('users:get-user-likes', kwargs={'slug': user_slug}) + f'?page={page_obj.next_page_number()}'
        # context['next_page_url'] = next_page_url
        
        # print(next_page_url)
        
        
        return context
    

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated:
        
            # Get the IDs of the liked quotes
            liked_quote_ids = QuotesLikes.objects.filter(user=user).values_list('quote_id', flat=True)

            # Retrieve the quotes based on their IDs and order them by the latest timestamp
            queryset = Quote.objects.filter(id__in=liked_quote_ids).select_related('author').annotate(latest_like_timestamp=Max('quoteslikes__timestamp')).order_by('-latest_like_timestamp')


            return queryset        
        else:
            # Redirect anonymous users to the login page
            # return redirect('users:login')
            raise PermissionDenied


    def get_template_names(self):
        if self.request.htmx:
            return ['quotes_cards.html']
        return ['get_user_likes.html']        
        



    # def render_to_response(self, context, **response_kwargs):
    #     if self.request.htmx:
    #         # If request is htmx, return the corresponding template
    #         template = self.get_template_names()
    #         return super().render_to_response(context, template=template, **response_kwargs)
    #     else:
    #         # If regular request, return normal response
    #         return super().render_to_response(context, **response_kwargs)
  

class UserRegisterView(generic.CreateView):
    form_class = UserCreationForm
    template_name = 'registration/register.html'
    success_url = reverse_lazy('users:login')
    
    
class LoginView(auth_views.LoginView):
    form_class = AuthenticationForm
    template_name = 'registration/login.html'
    

    def form_valid(self, form):
        # Call the parent form_valid method
        response = super().form_valid(form)

        # Retrieve the quote ID from the session
        quote_id = self.request.GET.get('quote_id')
        
        # If the quote ID exists, like the quote and redirect the user
        if quote_id:
            # Like the quote (add your logic here)
            like_quote(self.request, quote_id)
            
            # Redirect the user back to the initial page
            return redirect(reverse('users:get-user-likes', kwargs={'slug': self.request.user.slug}))
        

        return response  # Return the original response if no quote ID is found    
    
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
            #   print("1")
          else:
              translated_names[quote.id] = 'Unknown'
            #   print('2')
      
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

