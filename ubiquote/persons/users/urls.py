from django.urls import path, include
from . import views


app_name = 'users'

urlpatterns = [
    path('register/', views.UserRegisterView.as_view(), name='register'),
  
    # path('', include('django.contrib.auth.urls')),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),      
    
    path('users/', views.GetUsersView.as_view(), name='get-users'),
    path('user/<str:slug>/', views.GetUserView.as_view(), name='get-user'),
      
    path('update/user/<str:slug>/', views.UpdateUserView.as_view(), name='update-user'),
    path('delete/user/<str:slug>/', views.DeleteUserView.as_view(), name='delete-user'), 
    
    
    path('likes/<str:slug>/', views.GetUserLikesView.as_view(), name='get-user-likes'),        
  
    # path('add/user/', AddUserView.as_view(), name='add-user'),       
    
]
