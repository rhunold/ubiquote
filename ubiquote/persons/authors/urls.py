
from .views import GetAuthorsView, GetAuthorView , AddAuthorView, UpdateAuthorView , DeleteAuthorView, search_authors

from .views import author_list
from django.urls import path, include, re_path, reverse

# from persons.authors.models import AuthorAutocomplete

# from .models import AuthorAutocomplete


app_name = 'authors'

urlpatterns = [
    # path('', views.home, name='home'),
    
    # url(
    #     r'^author-autocomplete/$',
    #     AuthorAutocomplete.as_view(),
    #     name='author-autocomplete',
    # ),    
    
    # path(r'^author-autocomplete/$/', AuthorAutocomplete.as_view(), name='author-autocomplete'),
    
    # path('author-autocomplete/', AuthorAutocomplete.as_view(), name='author-autocomplete'),    
    
    path('authors/', GetAuthorsView.as_view(), name='get-authors'),
    path('author/<str:slug>/', GetAuthorView.as_view(), name='get-author'),
    path('add/author/', AddAuthorView.as_view(), name='add-author'),
    path('update/author/<str:slug>/', UpdateAuthorView.as_view(), name='update-author'),
    path('delete/author/<str:slug>/', DeleteAuthorView.as_view(), name='delete-author'),
    
    path('search_authors/', search_authors, name='search_authors'),
    path('author_list/', author_list, name='author_list'),    
   
]
