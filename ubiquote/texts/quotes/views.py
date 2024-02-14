from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView

from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.contrib import messages

from django.urls import reverse_lazy, reverse

from .models import Quote, QuotesLikes
from .forms import QuoteForm

from django.core.paginator import Paginator
from django.db.models import Count, Prefetch
from django.core.cache import cache


@login_required
def like_quote(request, id):
  quote = get_object_or_404(Quote, id=id)
  if quote.likes.filter(id=request.user.id).exists():
    quote.likes.remove(request.user)
  else:
    quote.likes.add(request.user)
  return HttpResponseRedirect(request.META['HTTP_REFERER'])


  
def get_user_quotes_likes(self, context):
  
  # Check if the cached data exists
  cached_data = cache.get('user_likes_{}'.format(self.request.user.id))
  if cached_data is not None:
      context['liked_quotes'] = cached_data
      return context
  
  # Prefetch related likes for all quotes
  quotes_with_likes = Quote.objects.annotate(
      total_likes=Count('likes')
  ).prefetch_related(
      Prefetch('likes', queryset=QuotesLikes.objects.filter(user=self.request.user), to_attr='user_likes')
  )

  # Determine which quotes are liked by the user
  liked_quotes = {quote.id: bool(quote.user_likes) for quote in quotes_with_likes}
  
  # Cache the data
  cache.set('user_likes_{}'.format(self.request.user.id), liked_quotes)  

  context['liked_quotes'] = liked_quotes
  
  # print(context)
  
  return context

class GetQuotesView(ListView):
  model = Quote
  template_name = 'get_quotes.html'
  context_object_name = 'quotes'
  # ordering =['-date_created']
  # status = 'published'
  # queryset = Quote.published.all()
  paginate_by = 10  # Number of items per page
  
  def get_queryset(self):
      # queryset = super().get_queryset().select_related('author',)
      queryset = Quote.objects.all().select_related('author').order_by('date_created')
      return queryset
  
  def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    
    # Get user likes for every like button on the page
    get_user_quotes_likes(self, context)
    
    context['user'] = self.request.user
      
    return context
  


class GetQuoteView(DetailView):
  model = Quote
  template_name = 'get_quote.html'
  context_object_name = 'quote'
  status = 'published'
  ordering =['-date_created']  
  
  def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)

    quote = self.object

    # Prefetch related likes for the provided quote
    liked_quotes = Quote.objects.filter(id=quote.id).annotate(
        total_likes=Count('likes')
    ).prefetch_related(
        Prefetch('likes', queryset=QuotesLikes.objects.filter(user=self.request.user), to_attr='user_likes')
    ).first()

    # Determine if the user has liked the provided quote
    context['liked_quotes'] = liked_quotes.user_likes
    context['count_likes'] = liked_quotes.total_likes if liked_quotes else 0  # Count likes or default to 0


    return context
  
  
 
class AddQuoteView(CreateView):
  model = Quote
  form_class = QuoteForm
  template_name = 'add_quote.html'
  # fields = '__all__'
  
  def get_success_url(self):
      # Redirect to the detail page of the newly created author
      return reverse_lazy('quotes:get-quote', kwargs={'slug': self.object.slug})  
  
  def form_valid(self, form):
      form.instance.contributor = self.request.user
      return super().form_valid(form)  
  
class UpdateQuoteView(UpdateView):
  model = Quote
  form_class = QuoteForm
  template_name = 'update_quote.html'
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
