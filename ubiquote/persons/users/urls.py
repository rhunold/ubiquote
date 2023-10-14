from django.urls import path, include
from .views import UserRegisterView, LoginView, GetUsersView, GetUserView, UpdateUserView, DeleteUserView, GetUserLikesView, LogoutView

app_name = 'users'

urlpatterns = [
    path('register/', UserRegisterView.as_view(), name='user-register'),
  
    # path('', include('django.contrib.auth.urls')),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),      
    
    path('users/', GetUsersView.as_view(), name='get-users'),
    path('user/<str:slug>/', GetUserView.as_view(), name='get-user'),
    path('user/<str:slug>/likes/', GetUserLikesView.as_view(), name='get-user-likes'),        
    path('update/user/<str:slug>/', UpdateUserView.as_view(), name='update-user'),
    path('delete/user/<str:slug>/', DeleteUserView.as_view(), name='delete-user'),   
  
    # path('add/user/', AddUserView.as_view(), name='add-user'),       
    
]
