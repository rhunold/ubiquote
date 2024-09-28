from django.urls import path
from . import views

app_name = 'texts'

urlpatterns = [
    # path('', views.home, name='home'),
    path('', views.HomeView.as_view(), name='get-home'),    
    
    path('categories/', views.GetCategoriesView.as_view(), name='get-categories'),
    # path('category/<int:pk>/', GetCategoryView.as_view(), name='get-category'),
    path('category/<str:slug>/', views.GetCategoryView.as_view(), name='get-category'),
]
