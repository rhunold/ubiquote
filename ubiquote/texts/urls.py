from django.urls import path
from . import views
from .views import home
from .views import GetCategoriesView, GetCategoryView

app_name = 'texts'

urlpatterns = [
    path('', views.home, name='home'),
    path('categories/', GetCategoriesView.as_view(), name='get-categories'),
    # path('category/<int:pk>/', GetCategoryView.as_view(), name='get-category'),
    path('category/<str:slug>/', GetCategoryView.as_view(), name='get-category'),
]
