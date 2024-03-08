from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView

from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from django.http import HttpResponseRedirect
from django.contrib import messages

from django.urls import reverse_lazy, reverse

from .models import Quote, QuotesLikes
from .forms import QuoteForm

from persons.authors.models import Author

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Count, Prefetch
from django.core.cache import cache
from django.contrib.auth import get_user_model
from django.conf import settings
from django.http import JsonResponse


@login_required
def like_quote(request, id):
    quote = get_object_or_404(Quote, id=id)
    if quote.likes.filter(id=request.user.id).exists():
        quote.likes.remove(request.user)
        liked = False
    else:
        quote.likes.add(request.user)
        liked = True
    likes_count = quote.likes.count()

    return render(request, 'like_quote.html', {'quote': quote, 'liked':liked})


class LanguageFilterMixin:
    def get_queryset(self, *args, **kwargs):
        queryset = super().get_queryset(*args, **kwargs)
                
        lang = self.request.LANGUAGE_CODE  # Get the language code from the request
        if lang == 'fr':
            queryset = queryset.filter(lang='fr')
        elif lang == 'en':
            queryset = queryset.filter(lang='en')
            
            
        # Retrieve the author slug from the kwargs 
        author_slug =  self.kwargs.get('slug')

        # If author slug is provided, filter queryset by author
        if author_slug:
            try:
                author = Author.objects.get(slug=author_slug)
                queryset = queryset.filter(author=author)
            except Author.DoesNotExist:
                # Handle case where author with given slug does not exist
                pass

                    
        return queryset

class GetQuotesView(LanguageFilterMixin, ListView):
    model = Quote
    template_name = 'get_quotes.html'
    context_object_name = 'quotes'
    ordering =['-date_created']
    # status = 'published'
    queryset = Quote.published.all().select_related('author')
    paginate_by = settings.DEFAULT_PAGINATION  # Number of items per page

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        user = self.request.user
        quotes = context['quotes']  # Get the queryset of quotes
        quotes_like_statut = {quote.id: QuotesLikes.has_user_liked(user, quote) for quote in quotes}
        liked_quotes = [quote_id for quote_id, liked in quotes_like_statut.items() if liked]  
        context['liked_quotes'] = liked_quotes      
                    
        # Get total number of quotes in the database
        total_quotes = Quote.objects.count()
        context['total_quotes'] = total_quotes
        
        return context
    


class GetQuoteView(DetailView):
    model = Quote
    template_name = 'get_quote.html'
    context_object_name = 'quote'
    status = 'published'
  
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['has_user_liked'] = QuotesLikes.has_user_liked(self.request.user, self.object) 
        return context
  

class AddQuoteView(CreateView):
    model = Quote
    form_class = QuoteForm
    template_name = 'add_quote.html'
    # fields = '__all__'
  
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_success_url(self):
        return reverse_lazy('quotes:get-quote', kwargs={'slug': self.object.slug})  
    
    def form_valid(self, form):
        form.instance.contributor = self.request.user
        return super().form_valid(form) 
    
class UpdateQuoteView(UpdateView):
    model = Quote
    form_class = QuoteForm
    template_name = 'update_quote.html'
    
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
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
    
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
