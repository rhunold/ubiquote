from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from django.http import HttpResponseRedirect, Http404

from django.contrib import messages

from django.urls import reverse_lazy, reverse

from .models import Quote, QuotesLikes
from .forms import QuoteForm

from django.db.models import Q

from persons.authors.models import Author

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Count, Prefetch
from django.core.cache import cache
from django.contrib.auth import get_user_model
from django.conf import settings

from django.http import JsonResponse
from django.contrib.postgres.search import SearchVector

from django.shortcuts import render
# from elasticsearch import Elasticsearch

from django.conf import settings
LANGUAGES = settings.LANGUAGES
from django.utils.translation import get_language


from django.template.loader import render_to_string
from django.http import HttpResponse


# from django.http import JsonResponse
from .services import RecommendationService

# @login_required
def like_quote(request, id):
    quote = get_object_or_404(Quote, id=id)
    
    
    if request.user.is_authenticated:
        if quote.likes.filter(id=request.user.id).exists():
            quote.likes.remove(request.user)
            liked = False
        else:
            quote.likes.add(request.user)
            liked = True
        likes_count = quote.likes.count()

        return render(request, 'like_quote.html', {'quote': quote, 'liked':liked})
    else:

        # quote_id = request.session['quote_id'] = quote.id
        # return redirect(reverse('users:login') + '?quote_id=' + str(quote_id) )

        # Store the quote ID in the session
        request.session['quote_id'] = id
        
        # Redirect the user to the login page with the quote ID included in the query string
        return redirect(reverse('users:login') + '?quote_id=' + str(id))        
        
    
    
     





def recommend_quotes(request, user_id):
    recommended_quotes = RecommendationService.recommend_quotes(user_id)
    return render(request, 'recommended_quotes.html', {'recommended_quotes': recommended_quotes})


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


class GetQuotesView(ListView, LanguageFilterMixin): # LoginRequiredMixin
    model = Quote
    template_name = 'get_quotes.html'
    context_object_name = 'quotes'
    ordering =['-date_created']
    # status = 'published'
    # queryset = Quote.published.all().select_related('author')
    paginate_by = settings.DEFAULT_PAGINATION  # Number of items per page

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        user = self.request.user # ATTENTION => si pas logué, page d'errreur => mettre en place redirection pour cas où on doit loguer l'utilisateur (avec un mixin, method_decoarator ou d'autre facon de faire... )
        
        
        quotes = context['quotes']  # Get the queryset of quotes
        quotes_like_statut = {quote.id: QuotesLikes.has_user_liked(user, quote) for quote in quotes}
        liked_quotes = [quote_id for quote_id, liked in quotes_like_statut.items() if liked]  
        context['liked_quotes'] = liked_quotes
        
        # Get translated names for authors
        if hasattr(self, 'request'):
            language_code = self.request.LANGUAGE_CODE
            # print(language_code)
        else:
            language_code = 'en'  # Default language if language code is not available
        
        translated_names = {}
        for quote in quotes:
            author = quote.author
            if author:
                translated_names[quote.id] = author.get_translation(language_code)
            else:
                translated_names[quote.id] = 'Unknown'
        
        # print(translated_names)
        context['translated_names'] = translated_names
           
                    
        # Get total number of quotes in the database
        total_quotes = Quote.objects.count()
        context['total_quotes'] = total_quotes
        
        # GET the search query / create pagination
        search_query = self.request.GET.get('q')
        context['search_query'] = search_query
        if search_query:
            paginator = Paginator(self.get_queryset(), self.paginate_by)
            page_number = self.request.GET.get('page')
            page_obj = paginator.get_page(page_number)
            context['page_obj'] = page_obj
            context['paginator'] = paginator
        
        return context
        
    def get_queryset(self):
        queryset = super().get_queryset()  # Get the default queryset
        search_query = self.request.GET.get('q')
        if search_query:
            queryset = queryset.annotate(
                search=SearchVector('text')
            ).filter(search=search_query)
        return queryset
        
    # REdirect if page number requested is empty
    def get(self, request, *args, **kwargs):
        # print(dir(request))
        try:
            return super().get(request, *args, **kwargs)

        except Http404:
            page = self.request.GET.get('page', None)
            paginator = Paginator(self.get_queryset(), self.paginate_by)
            last_page = paginator.num_pages or 1
            search_query = self.request.GET.get('q') or ''
            if page:
                return HttpResponseRedirect(reverse('quotes:get-quotes') + f'?q={search_query}&page={last_page}')
            else:
                raise        


class GetQuoteView(DetailView): # LoginRequiredMixin
    model = Quote
    template_name = 'get_quote.html'
    context_object_name = 'quote'
    status = 'published'
  
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['has_user_liked'] = QuotesLikes.has_user_liked(self.request.user, self.object) 
        
        quote = self.object
        
        # Get translated names for authors
        if hasattr(self, 'request'):
            language_code = self.request.LANGUAGE_CODE
            # print(language_code)
        else:
            language_code = 'en'  # Default language if language code is not available        
        
        # Assuming the Quote model has a foreign key field named 'author'
        author = quote.author  # Retrieve the author associated with the quote
        
        # Assuming LANGUAGES is defined elsewhere
        if author:
            translated_names = {}
            translated_names[quote.id] = author.get_translation(language_code)
            context['translated_names'] = translated_names
        else:
            pass
        
        return context
  

class AddQuoteView(LoginRequiredMixin, CreateView):
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
 
# @login_required   
class UpdateQuoteView(LoginRequiredMixin, UpdateView):
    model = Quote
    form_class = QuoteForm
    template_name = 'update_quote.html'
    
    # @method_decorator(login_required)
    # def dispatch(self, *args, **kwargs):
    #     return super().dispatch(*args, **kwargs)
    
    # fields = '__all__'  
    def get_success_url(self):
        # Redirect to the detail page of the newly created author
        return reverse_lazy('quotes:get-quote', kwargs={'slug': self.object.slug})

@login_required
class DeleteQuoteView(DeleteView):
    model = Quote
    # form_class = QuoteForm
    template_name = 'delete_quote.html'
    success_url = reverse_lazy('quotes:get-quotes')
    # fields = '__all__' 
    
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
