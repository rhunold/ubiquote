from django.urls import path
# from . import views
from .views import GetAuthorsView, GetAuthorView # , AddAuthorView, UpdateAuthorView, DeleteAuthorView
from django.urls import path, include, re_path

app_name = 'authors'

urlpatterns = [
    # path('', views.home, name='home'),
    path('authors/', GetAuthorsView.as_view(), name='get-authors'),
    path('author/<str:slug>/', GetAuthorView.as_view(), name='get-author'),
    # path('author/add/', AddAuthorView.as_view(), name='add-quote'),
    # path('author/update/<int:pk>', UpdateAuthorView.as_view(), name='update-author'),
    # path('author/delete/<int:pk>', DeleteAuthorView.as_view(), name='delete-author'),        
]
