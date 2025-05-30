from django.urls import path
from django.urls import re_path
from . import views

app_name = 'quotes'

urlpatterns = [
    
    path('quotes/', views.GetQuotesView.as_view(), name='get-quotes'),
    
    # path('<str:author_slug>/<str:slug>/', views.GetQuoteView.as_view(), name='get-quote'),
    path('quote/<str:slug>/', views.GetQuoteView.as_view(), name='get-quote'),
    
    # path('quote/<str:slug_with_id>/', views.GetQuoteView.as_view(), name='get-quote'),    
    
    
    path('add/quote/', views.AddQuoteView.as_view(), name='add-quote'),
    path('update/quote/<str:slug>/', views.UpdateQuoteView.as_view(), name='update-quote'),
    path('delete/quote/<str:slug>/', views.DeleteQuoteView.as_view(), name='delete-quote'),

    
    path('quote/like/<int:id>/', views.like_quote, name='like_quote'),  
    
    # path('<str:author_slug>/<str:slug>/img/', views.GetQuoteView.as_view(), name='get-img_quote'),    
    path('quote/<str:slug>/img/', views.GetQuoteView.as_view(), name='get-img_quote'),      
      
    # path('recommendations/<int:user_id>/', views.recommend_quotes, name='recommend-quotes'),
    
    # path('author/<str:slug>/', views.GetAuthorView.as_view(), name='author-quotes'),

]
