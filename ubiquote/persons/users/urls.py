from django.urls import path, include
from .views import UserRegisterView, LoginView #, LogoutView


app_name = 'users'

urlpatterns = [
    path('register/', UserRegisterView.as_view(), name='user-register'),
    # path('login/', LoginView.as_view(), name='login'),
    path('', include('django.contrib.auth.urls')),     
    
    # path('logout/', LogoutView.as_view(), name='logout'),    
    # path('users/', GetUserView.as_view(), name='get-users'),
    # path('user/<int:pk>', GetQuotetView.as_view(), name='get-quote'),
    # path('user/add/', AddQuoteView.as_view(), name='add-quote'),
    # path('user/update/<int:pk>', UpdateQuoteView.as_view(), name='update-quote'),
    # path('user/delete/<int:pk>', DeleteQuoteView.as_view(), name='delete-quote'),    
    
]
