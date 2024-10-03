from django.urls import path
from . import views
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

app_name = 'api'

urlpatterns = [
    
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),   
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),     
    
    path("", views.HomeQuotesAPIView.as_view(), name="home-api-view"),
    
    
    path("quotes/", views.QuotesAPIView.as_view(), name="quotes-list-api-view"),
    path("quote/<int:id>/", views.QuoteAPIView.as_view(), name="quote-api-view"),
    
    path("categories/", views.CategoriesAPIView.as_view(), name="categories-list-api-view"),
    path("category/<str:slug>/", views.CategoryAPIView.as_view(), name="category-api-view"),
    
    path("category/<str:slug>/quotes/", views.CategoryQuotesAPIView.as_view(), name="category-quotes-api-view"),        
    
    
    path("authors/", views.AuthorsAPIView.as_view(), name="authors-list-api-view"),
    path("author/<str:slug>/", views.AuthorAPIView.as_view(), name="author-api-view"),        
    path('author/quotes/<str:slug>/', views.AuthorQuotesAPIView.as_view(), name='author-quotes-api-view'),

    path("users/", views.UsersAPIView.as_view(), name="users-list-api-view"),    
    path("user/<str:slug>/", views.UserAPIView.as_view(), name="user-api-view"),   # User info
    
    path('user/<str:slug>/quotes/', views.UserQuotesContributorAPIView.as_view(), name='user-quotes-contributor-api-view'), # Quote with contributor is user
    
    path('likes/<str:slug>/', views.UserQuotesLikesAPIView.as_view(), name='user-quotes-likes-api-view'),   
        
    
    # path('quote/like/<int:id>/', views.QuotesLikesAPIView.as_view(), name='like-quote'),    
    
    # path('quote/like/<int:id>/', like_quote, name='like-quote'),    
       
           
    # path('quote/<int:quote_id>/like/', LikeQuoteAPIView.as_view(), name='like-quote'),

]