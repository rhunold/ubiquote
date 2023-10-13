
from .views import GetAuthorsView, GetAuthorView , AddAuthorView, UpdateAuthorView , DeleteAuthorView
from django.urls import path, include, re_path

app_name = 'authors'

urlpatterns = [
    # path('', views.home, name='home'),
    path('authors/', GetAuthorsView.as_view(), name='get-authors'),
    path('author/<str:slug>/', GetAuthorView.as_view(), name='get-author'),
    path('add/author/', AddAuthorView.as_view(), name='add-author'),
    path('update/author/<str:slug>/', UpdateAuthorView.as_view(), name='update-author'),
    path('delete/author/<str:slug>/', DeleteAuthorView.as_view(), name='delete-author'),        
]
