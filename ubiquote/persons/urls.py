from django.urls import path
from . import views
from django.urls import path, include, re_path

app_name = 'persons'

urlpatterns = [
    # path('', views.home, name='home'),
    path('', include('quotes.urls', namespace='quotes')),    
    
]
