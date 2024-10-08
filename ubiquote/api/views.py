from django.shortcuts import render, get_object_or_404, redirect
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly, AllowAny
from rest_framework.exceptions import NotAuthenticated

from django.template.loader import render_to_string
from django.http import HttpResponse


from django.db.models import Q
from texts.quotes import models as QuoteModel
from persons.authors import models as AuthorModel
from persons.users import models as UserModel

from django.db.models import Count

from texts.models import Category
from texts.quotes.services import RecommendationService

from .serializers import QuoteSerializer, AuthorSerializer, UserSerializer, ShortAuthorSerializer, ShortUserSerializer,  ShortQuoteSerializer, ShortQuotesLikesSerializer, CategorySerializer

# import . from serializers

class CustomPagination(PageNumberPagination):
    page_size = 10  # Number of quotes per page
    page_size_query_param = 'page_size'
    
    
    # def get_paginated_response(self, data):
    #     return Response({
    #         'links': {
    #            'next': self.get_next_link(),
    #            'previous': self.get_previous_link()
    #         },
    #         'count': self.page.paginator.count,
    #         'results': data
    #     })
    

class QuotesAPIView(generics.ListAPIView):
    # queryset = QuoteModel.Quote.objects.all()
    serializer_class = QuoteSerializer
    pagination_class = CustomPagination    
    permission_classes = [AllowAny]    
    
    
    def get_queryset(self):
        queryset = QuoteModel.Quote.objects.all()
        
        # Get the search query from the request
        search_query = self.request.query_params.get('q', None)
        
        if search_query:
            # Filter the quotes based on the search query
            queryset = queryset.filter(
                Q(text__icontains=search_query) |
                Q(author__fullname__icontains=search_query) 
            )
        
        # print(queryset)
        return queryset 
    
    
    
        
    # queryset = models.Quote.objects.all().order_by('-date_created') 
    
    def get_serializer_context(self):
        # Pass the request context to serializer to access request parameters
        return {'request': self.request}    
    
class QuoteAPIView(generics.RetrieveAPIView):
    # queryset = QuoteModel.Quote.objects.all()
    queryset = QuoteModel.Quote.objects.all()
    serializer_class = QuoteSerializer
    lookup_field = "id"
    permission_classes = [AllowAny]        
    
    
class AuthorAPIView(generics.RetrieveAPIView):
    # queryset = QuoteModel.Quote.objects.all()
    pagination_class = CustomPagination       
    queryset = AuthorModel.Author.objects.all()
    serializer_class = AuthorSerializer
    lookup_field = "slug"    
    permission_classes = [AllowAny]        


class AuthorsAPIView(generics.ListAPIView):
    serializer_class = ShortAuthorSerializer
    pagination_class = CustomPagination    
    permission_classes = [AllowAny]        
    
    
    def get_queryset(self):
        queryset = AuthorModel.Author.objects.all()
        
        # Get the search query from the request
        search_query = self.request.query_params.get('q', None)
        
        if search_query:
            # Filter the quotes based on the search query
            queryset = queryset.filter(
                # Q(text__icontains=search_query) |
                Q(fullname__icontains=search_query) 
            )
        
        # print(queryset)
        return queryset 
        
    
    def get_serializer_context(self):
        # Pass the request context to serializer to access request parameters
        return {'request': self.request}   

class AuthorQuotesAPIView(generics.ListAPIView):
    """
    API view to retrieve quotes for a specific author using the author's slug.
    """
    
    serializer_class = ShortQuoteSerializer
    pagination_class = CustomPagination  
    permission_classes = [AllowAny]        


    def get_queryset(self):
        # Get the author slug from the URL
        author_slug = self.kwargs.get('slug')

        # Ensure the author slug is provided
        if not author_slug:
            raise serializers.ValidationError({"detail": "Author slug is required."})

        # Return the filtered queryset based on the author's slug
        return QuoteModel.Quote.objects.filter(author__slug=author_slug)
    
    
    
    
    

class UsersAPIView(generics.ListAPIView):
    serializer_class = ShortUserSerializer
    pagination_class = CustomPagination  
    permission_classes = [AllowAny]          
    
    
    def get_queryset(self):
        queryset = UserModel.User.objects.all()
        
        # Get the search query from the request
        search_query = self.request.query_params.get('q', None)
        
        if search_query:
            # Filter the quotes based on the search query
            queryset = queryset.filter(
                # Q(text__icontains=search_query) |
                Q(username__icontains=search_query) 
            )
        
        # print(queryset)
        return queryset 
        
    
    def get_serializer_context(self):
        # Pass the request context to serializer to access request parameters
        return {'request': self.request}   
    
    
class UserAPIView(generics.RetrieveAPIView):
    pagination_class = CustomPagination       
    queryset = UserModel.User.objects.all()
    serializer_class = UserSerializer
    lookup_field = "slug"   
    permission_classes = [AllowAny]        
    
    

class UserQuotesContributorAPIView(generics.ListAPIView):
    """
    API view to retrieve quotes for a specific contributor with the user's slug.
    """
    
    serializer_class = ShortQuoteSerializer
    pagination_class = CustomPagination  
    permission_classes = [AllowAny]        
    # contributor = ShortUserSerializer   
    # likes = QuotesLikesSerializer  


    def get_queryset(self):
        # Get the user slug from the URL
        user_slug = self.kwargs.get('slug')

        # Ensure the user slug is provided
        if not user_slug:
            raise serializers.ValidationError({"detail": "User slug is required."})

        # Return the filtered queryset based on the user's slug
        return QuoteModel.Quote.objects.filter(contributor__slug=user_slug)
    
    

class UserQuotesLikesAPIView(generics.ListAPIView):
    """
    API view to list quotes that a user has liked.
    """    
    serializer_class = ShortQuoteSerializer  # Use the quote serializer
    pagination_class = CustomPagination  # Optional: Pagination class to control how many quotes per page
    permission_classes = [AllowAny]    

    def get_queryset(self):
        # Get the user slug from the URL
        profil_slug = self.kwargs.get('slug')
        
        # Get the user profile
        try:
            profil = UserModel.User.objects.get(slug=profil_slug)
        except UserModel.User.DoesNotExist:
            raise serializers.ValidationError({"detail": "User does not exist."})

        # Get all the quote IDs that the user has liked
        liked_quotes_ids = QuoteModel.QuotesLikes.objects.filter(user=profil).values_list('quote', flat=True)

        # Return the queryset of quotes the user has liked
        return QuoteModel.Quote.objects.filter(id__in=liked_quotes_ids)
    
    
    
    

    # def get(self, request, id):
    #     # Get the quote
    #     quote = QuoteModel.Quote.objects.get(id=id)
    #     user = request.user
        
    #     # Check if the quote is liked by the user
    #     # has_user_liked = QuoteModel.QuotesLikes.objects.filter(user=user, quote=quote).exists()

    #     # # Serialize the quote and pass the request to the context
    #     serializer = ShortQuoteSerializer(quote, context={'request': request})

    #     # Return the serialized data with the like status
    #     return Response(serializer.data)    

class UserLikesAPIView(generics.GenericAPIView):
    """
    API view to allow a user to like or dislike a quote
    """
        
    pagination_class = CustomPagination    
    serializer_class = ShortQuoteSerializer       
    permission_classes = [IsAuthenticated]
    
    
    def get(self, request, id):
        # Get the quote
        quote = QuoteModel.Quote.objects.get(id=id)
        user = request.user
        
        # Check if the quote is liked by the user
        has_user_liked = QuoteModel.QuotesLikes.objects.filter(user=user, quote=quote).exists()

        # # Serialize the quote and pass the request to the context
        # serializer = ShortQuoteSerializer(quote, context={'request': request})

        # Return the serialized data with the like status
        return Response(serializer.data)
    
    
# def get_object(self):
#     queryset = self.get_queryset()
#     filter = {}
#     for field in self.multiple_lookup_fields:
#         filter[field] = self.kwargs[field]

#     obj = get_object_or_404(queryset, **filter)
#     self.check_object_permissions(self.request, obj)
#     return obj    
    

    def post(self, request, id):
        quote = QuoteModel.Quote.objects.get(id=id)
        user = request.user

        # Check if the user already liked the quote
        liked = QuoteModel.QuotesLikes.objects.filter(user=user, quote=quote).exists()
        
        if liked:
            # Unlike the quote
            QuoteModel.QuotesLikes.objects.filter(user=user, quote=quote).delete()
            # has_user_liked = False
        else:
            # Like the quote
            QuoteModel.QuotesLikes.objects.create(user=user, quote=quote)
            # has_user_liked = True

        # Update the likes count
        likes = quote.likes.count()
        
        # Update the list of user who like the quote        
        # likes = quote.likes.append(user.id)


        # Render the updated like area using the partial template
        context = {
            'quote': quote,
            'quote.likes': likes,
            # 'likes_count': likes_count,
            # 'has_user_liked': has_user_liked
        }
        
        # print(context)
        
        
        return render(request, 'like_quote.html', context)
    
    
class QuoteAPIView(generics.RetrieveAPIView):
    # queryset = QuoteModel.Quote.objects.all()
    queryset = QuoteModel.Quote.objects.all()
    serializer_class = QuoteSerializer
    lookup_field = "id"    
    permission_classes = [AllowAny]        
    

class CategoriesAPIView(generics.ListAPIView):
    # queryset = QuoteModel.Quote.objects.all()
    serializer_class = CategorySerializer
    pagination_class = CustomPagination  
    permission_classes = [AllowAny]          
    
    def get_queryset(self):
        queryset = Category.objects.all()
        
        # Get the search query from the request
        search_query = self.request.query_params.get('q', None)
        
        if search_query:
            # Filter the quotes based on the search query
            queryset = queryset.filter(
                Q(text__icontains=search_query) |
                Q(title__icontains=search_query) 
            )
        
        # print(queryset)
        return queryset 
        
    # queryset = models.Quote.objects.all().order_by('-date_created') 
    
    def get_serializer_context(self):
        # Pass the request context to serializer to access request parameters
        return {'request': self.request}    


class CategoryQuotesAPIView(generics.ListAPIView):
    serializer_class = ShortQuoteSerializer  # Use the quote serializer
    pagination_class = CustomPagination  # Optional: Pagination class to control how many quotes per page
    permission_classes = [AllowAny]    
    
    def get_queryset(self):
        # Get the category ID from the URL

        category_slug = self.kwargs.get('slug')    
        category = get_object_or_404(Category, slug=category_slug)
     
        
        # Get all the quote IDs that belong to this category
        category_quotes = QuoteModel.QuotesCategories.objects.filter(category=category).values_list('quote', flat=True)
        
        queryset = QuoteModel.Quote.objects.filter(id__in=category_quotes)
        
        # print(type(queryset))

        # Return the queryset of quotes that belong to the category
        return queryset
    

    
    
    

class CategoryAPIView(generics.RetrieveAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    lookup_field = "slug"    
    permission_classes = [AllowAny]   
    
    

class HomeQuotesAPIView(generics.ListAPIView):
    """
    API list view recommanded quotes to user based on his previous likes 
    OR 100 most liked quotes for anonymous or not quote liked yet
    """    
    serializer_class = QuoteSerializer
    pagination_class = CustomPagination
    # permission_classes = [IsAuthenticated]   
    permission_classes = [IsAuthenticatedOrReadOnly]       


    def get_queryset(self):
        # Check if user is authenticated
        if self.request.user.is_authenticated:
            print("There is a permission ")
            user_id = self.request.user.id
            recommended_quotes = RecommendationService.recommend_quotes(user_id)
            print(type(recommended_quotes))
        else:
        # Handle anonymous user case by showing popular quotes
            print("There is no permission ")
            recommended_quotes = QuoteModel.Quote.objects.annotate(num_likes=Count('quoteslikes')).order_by('-num_likes')[:100]
            print(recommended_quotes)
            print(type(recommended_quotes))
                
        # recommended_quotes = Quote.objects.annotate(num_likes=Count('quoteslikes')).order_by('-num_likes')[:100]
    

        return recommended_quotes

    # Optionally, raise an error if you want to restrict this to authenticated users
    # def get(self, request, *args, **kwargs):
    #     if not request.user.is_authenticated:
    #         raise NotAuthenticated("You must be logged in to view recommendations.")
        

    #     return super().get(request, *args, **kwargs)