from django.urls import path
from .views import GetQuotesView, GetQuoteView, AddQuoteView, UpdateQuoteView, DeleteQuoteView, like_quote #, like_unlike_quote
from django.urls import re_path

app_name = 'quotes'

urlpatterns = [
    path('quotes/', GetQuotesView.as_view(), name='get-quotes'),
    path('quote/<str:slug>', GetQuoteView.as_view(), name='get-quote'),
    path('add/quote/', AddQuoteView.as_view(), name='add-quote'),
    path('update/quote/<str:slug>', UpdateQuoteView.as_view(), name='update-quote'),
    path('delete/quote/<str:slug>', DeleteQuoteView.as_view(), name='delete-quote'),
    path('like/<int:id>/', like_quote, name='like-quote'),    
    # path('like-unlike-quote/<int:quote_id>/', like_unlike_quote, name='like-unlike-quote'),

]
