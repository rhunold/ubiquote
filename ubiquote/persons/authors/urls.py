
# from .views import GetAuthorsView, GetAuthorView , AddAuthorView, UpdateAuthorView , DeleteAuthorView 
from . import views

# from .views import search_authors, author_list
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
    
    # path(r'^author-autocomplete/$/', views.AuthorAutocomplete.as_view(), name='author-autocomplete'),
    
    # path('author-autocomplete/', views.AuthorAutocomplete.as_view(), name='author-autocomplete'),    
    
    path('authors/', views.GetAuthorsView.as_view(), name='get-authors'),
    path('author/<str:slug>/', views.GetAuthorView.as_view(), name='get-author'),
    path('add/author/', views.AddAuthorView.as_view(), name='add-author'),
    path('update/author/<str:slug>/', views.UpdateAuthorView.as_view(), name='update-author'),
    path('delete/author/<str:slug>/', views.DeleteAuthorView.as_view(), name='delete-author'),
    
    # path('search_authors/',views.search_authors, name='search_authors'),
    # path('author_list/', views.author_list, name='author_list'),    
   
]
