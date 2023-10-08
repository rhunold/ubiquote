from django.urls import path
from . import views
from .views import GetQuotestView, GetQuotetView, AddQuoteView, UpdateQuoteView, DeleteQuoteView
from django.urls import re_path

app_name = 'quotes'

urlpatterns = [
    path('quotes/', GetQuotestView.as_view(), name='get-quotes'),
    path('quote/<int:pk>', GetQuotetView.as_view(), name='get-quote'),
    path('quote/add/', AddQuoteView.as_view(), name='add-quote'),
    path('quote/update/<int:pk>', UpdateQuoteView.as_view(), name='update-quote'),
    path('quote/delete/<int:pk>', DeleteQuoteView.as_view(), name='delete-quote'),    
    
]
