from django.urls import path
from django.urls import re_path
from .views import GetQuotesView, GetQuoteView, AddQuoteView, UpdateQuoteView, DeleteQuoteView #, like_unlike_quote
from .views import like_quote #, search_quotes, quote_result

app_name = 'quotes'

urlpatterns = [
    path('quotes/', GetQuotesView.as_view(), name='get-quotes'),
    path('quote/<str:slug>', GetQuoteView.as_view(), name='get-quote'),
    path('add/quote/', AddQuoteView.as_view(), name='add-quote'),
    path('update/quote/<str:slug>', UpdateQuoteView.as_view(), name='update-quote'),
    path('delete/quote/<str:slug>', DeleteQuoteView.as_view(), name='delete-quote'),
    
  
    # function to add / remove a like on a quote
    path('quote/like/<int:id>/', like_quote, name='like-quote'),
    
    
    # path('search/', search_quotes, name='search-quotes'),  
        
    # path('search_quotes/', search_quotes, name='search-quotes'),
    # path('quote_results/', quote_results, name='quote-results'),     
    
    # path('search/', search, name='search'),    
    

]
