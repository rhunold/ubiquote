from django.urls import path
from django.urls import re_path
from . import views

app_name = 'quotes'

urlpatterns = [
    path('quotes/', views.GetQuotesView.as_view(), name='get-quotes'),
    path('quote/<str:slug>', views.GetQuoteView.as_view(), name='get-quote'),
    path('add/quote/', views.AddQuoteView.as_view(), name='add-quote'),
    path('update/quote/<str:slug>', views.UpdateQuoteView.as_view(), name='update-quote'),
    path('delete/quote/<str:slug>', views.DeleteQuoteView.as_view(), name='delete-quote'),

    
    path('quote/like/<int:id>/', views.like_quote, name='like_quote'),    
    path('recommendations/<int:user_id>/', views.recommend_quotes, name='recommend-quotes'),
     
    # function to add / remove a like on a quote
    # path('quote/like/<int:id>/', views.like_quote, name='like-quote'),     
    # path('search/', views.search_quotes, name='search-quotes'),  
    # path('search_quotes/', views.search_quotes, name='search-quotes'),
    # path('quote_results/', views.quote_results, name='quote-results'),     
    # path('search/', views.search, name='search'),    
    

]
