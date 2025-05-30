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

import random
from django.db.models import Case, Value, When

from django.db.models import Q
from texts.quotes import models as QuoteModel
from persons.authors import models as AuthorModel
from persons.users import models as UserModel

# from texts.quotes.forms import QuoteForm
from texts.quotes.utils import QuoteDuplicateException
from rest_framework.exceptions import ValidationError

from django.db.models import Count

from texts.models import Category
from texts.quotes.services import RecommendationService

from .serializers import QuoteSerializer, AuthorSerializer, UserSerializer, ShortAuthorSerializer, ShortUserSerializer,  ShortQuoteSerializer, ShortQuotesLikesSerializer, CategorySerializer, QuoteRecommandSerializer

from texts.quotes.utils import clean_text
from django.db import transaction
from texts.quotes.utils import generate_response

from django.utils.translation import get_language

import base64, os, time, threading
from uuid import uuid4
from django.conf import settings

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
    
class CustomCategoriesPagination(PageNumberPagination):
    page_size = 20  # Number of quotes per page
    page_size_query_param = 'page_size'

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
                Q(text__icontains=search_query) 
                # | Q(author__fullname__icontains=search_query) 
            )
        
        # print(queryset)
        return queryset 
    
    
    
        
    # queryset = models.Quote.objects.all().order_by('-date_created') 
    
    def get_serializer_context(self):
        # Pass the request context to serializer to access request parameters
        return {'request': self.request}    
    
# class QuoteAPIView(generics.RetrieveAPIView):
#     # queryset = QuoteModel.Quote.objects.all()
#     queryset = QuoteModel.Quote.objects.all()
#     serializer_class = QuoteSerializer
#     lookup_field = "id"
#     permission_classes = [AllowAny]        
    
    
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
    
    serializer_class = QuoteSerializer
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
    
    serializer_class = QuoteSerializer
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
    serializer_class = QuoteSerializer  # Use the quote serializer
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


# class UserLikesAPIView(generics.GenericAPIView):
#     """
#     API view to allow a user to like or dislike a quote
#     """
        
#     pagination_class = CustomPagination    
#     serializer_class = ShortQuoteSerializer       
#     permission_classes = [IsAuthenticated]
    
    
#     def get(self, request, id):
#         # Get the quote
#         quote = QuoteModel.Quote.objects.get(id=id)
#         user = request.user
        
#         # Check if the quote is liked by the user
#         has_user_liked = QuoteModel.QuotesLikes.objects.filter(user=user, quote=quote).exists()

#         # # Serialize the quote and pass the request to the context
#         # serializer = ShortQuoteSerializer(quote, context={'request': request})

#         # Return the serialized data with the like status
#         return Response(serializer.data)
    
    
# # def get_object(self):
# #     queryset = self.get_queryset()
# #     filter = {}
# #     for field in self.multiple_lookup_fields:
# #         filter[field] = self.kwargs[field]

# #     obj = get_object_or_404(queryset, **filter)
# #     self.check_object_permissions(self.request, obj)
# #     return obj    
    

#     def post(self, request, id):
#         quote = QuoteModel.Quote.objects.get(id=id)
#         user = request.user

#         # Check if the user already liked the quote
#         liked = QuoteModel.QuotesLikes.objects.filter(user=user, quote=quote).exists()
        
#         if liked:
#             # Unlike the quote
#             QuoteModel.QuotesLikes.objects.filter(user=user, quote=quote).delete()
#             # has_user_liked = False
#         else:
#             # Like the quote
#             QuoteModel.QuotesLikes.objects.create(user=user, quote=quote)
#             # has_user_liked = True

#         # Update the likes count
#         likes = quote.likes.count()
        
#         # Update the list of user who like the quote        
#         # likes = quote.likes.append(user.id)


#         # Render the updated like area using the partial template
#         context = {
#             'quote': quote,
#             'quote.likes': likes,
#             # 'likes_count': likes_count,
#             # 'has_user_liked': has_user_liked
#         }
        
#         # print(context)
        
        
#         return render(request, 'like_quote.html', context)
    

class QuoteAPIView(generics.RetrieveAPIView):
    # queryset = QuoteModel.Quote.objects.all()
    queryset = QuoteModel.Quote.objects.all()
    serializer_class = QuoteSerializer
    lookup_field = "id"    
    permission_classes = [AllowAny]     
    

    def post(self, request, id):
        image_data = request.data.get("image")
        # print("Incoming POST:", request.data)
        
        if not image_data:
            return Response({"error": "No image provided"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            format, imgstr = image_data.split(';base64,')
            ext = format.split('/')[-1]
            filename = f"{uuid4().hex}.{ext}"
            save_dir = os.path.join(settings.MEDIA_ROOT, 'generated')
            os.makedirs(save_dir, exist_ok=True)

            file_path = os.path.join(save_dir, filename)
            with open(file_path, "wb") as f:
                f.write(base64.b64decode(imgstr))

            # Auto-delete after 5 min
            def delete_later(path, delay=300):
                time.sleep(delay)
                if os.path.exists(path):
                    os.remove(path)
            threading.Thread(target=delete_later, args=(file_path,)).start()

            image_url = request.build_absolute_uri(f"{settings.MEDIA_URL}generated/{filename}")
            return Response({"image_url": image_url}, status=status.HTTP_201_CREATED)
        
            # return Response({"image_url": request.build_absolute_uri(url)})        

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
       
    

class CategoriesAPIView(generics.ListAPIView):
    # queryset = QuoteModel.Quote.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [AllowAny]          

    pagination_class = CustomCategoriesPagination  
    
    
    def get_queryset(self):

        queryset = Category.objects.annotate(quotes_count=Count('quote'))
        
        # for cat in queryset.all():
        #     print(cat.title, cat.slug)   
        
        # Get the search query from the request
        search_query = self.request.query_params.get('q', None)
        
        if search_query:
            # Filter the quotes based on the search query
            queryset = queryset.filter(
                Q(text__icontains=search_query) |
                Q(title__icontains=search_query) 
            )
        
        # print(queryset)
        
        lang = self.request.GET.get("lang") or get_language()
        order_field = f"title_{lang}" if lang != "en" else "title"  
        
        # print("Language in API view:", get_language())      
        
        return queryset.order_by(order_field) # for alphabetical sort
        
    # # queryset = models.Quote.objects.all().order_by('-date_created') 
    
    # def get_serializer_context(self):
    #     # Pass the request context to serializer to access request parameters
    #     return {'request': self.request}    


class CategoryQuotesAPIView(generics.ListAPIView):
    serializer_class = QuoteSerializer  # Use the quote serializer
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
    # queryset = QuoteModel.UserQuoteRecommendation.objects.all()
    # serializer_class = QuoteRecommandSerializer
    serializer_class = QuoteSerializer    
    
    permission_classes = [IsAuthenticatedOrReadOnly] # [AllowAny] [IsAuthenticated]
    pagination_class = CustomPagination
    # ordering = ['?']     



    def get_queryset(self):
        if self.request.user.is_authenticated:
            # Get the user profile
            try:
                user = UserModel.User.objects.get(id=self.request.user.id)
            except UserModel.User.DoesNotExist:
                raise serializers.ValidationError({"detail": "User does not exist."})

            # Get all the quote IDs recommanded to the user except if not like any quote yet
            if not QuoteModel.UserQuoteRecommendation.objects.filter(user=user).exists():
                recommended_quotes = QuoteModel.Quote.objects.annotate(num_likes=Count('quoteslikes')).order_by('-num_likes')[:100]
            else:
                recommanded_quotes_ids = QuoteModel.UserQuoteRecommendation.objects.filter(user=user).values_list('quote', flat=True)
                liked_quotes = QuoteModel.QuotesLikes.objects.filter(user=user).values_list('quote__id', flat=True)                
                recommended_quotes = QuoteModel.Quote.objects.filter(id__in=recommanded_quotes_ids).exclude(id__in=liked_quotes)
                
                        
                # Shuffle the queryset for each session
                session_key = 'shuffled_quote_ids'
                if session_key not in self.request.session:
                    # Shuffle only once per session
                    quote_ids = list(recommended_quotes.values_list('id', flat=True))
                    random.shuffle(quote_ids)
                    self.request.session[session_key] = quote_ids

                # Get the shuffled quote IDs from session and maintain order
                shuffled_ids = self.request.session[session_key]
                recommended_quotes = QuoteModel.Quote.objects.filter(id__in=shuffled_ids).order_by(Case(*[When(id=id, then=pos) for pos, id in enumerate(shuffled_ids)]))                
                            

        else:
        # Handle anonymous user case by showing popular quotes
            recommended_quotes = QuoteModel.Quote.objects.annotate(num_likes=Count('quoteslikes')).order_by('-num_likes')[:100]

        return recommended_quotes
    


    # def get_queryset(self):
    #     # Check if user is authenticated
    #     if self.request.user.is_authenticated:

    #         # user_id = self.request.user.id
    #         # recommended_quotes = RecommendationService.recommend_quotes(user_id)
            
    #         user = self.request.user            
    #         recommended_quotes = QuoteModel.UserQuoteRecommendation.objects.filter(user=user)
    #         print("TEST")
            
            
    #     else:
    #     # Handle anonymous user case by showing popular quotes
    #         recommended_quotes = QuoteModel.Quote.objects.annotate(num_likes=Count('quoteslikes')).order_by('-num_likes')[:100]
    #         # recommended_quotes = QuoteModel.Quote.objects.all()[:100]
            
    #         print("Hello")


    #     return recommended_quotes





    # def get_queryset(self):
    #     if self.request.user.is_authenticated:
    #         user = self.request.user
    #         recommended_quotes = QuoteModel.UserQuoteRecommendation.objects.filter(user=user).order_by('id')  # Ensure it's ordered
    #         return recommended_quotes
    #     else:
    #         recommended_quotes = QuoteModel.Quote.objects.annotate(num_likes=Count('quoteslikes')).order_by('-num_likes')[:100]
    #         return recommended_quotes            
            


    # def get_queryset(self):
    #     # Check if user is authenticated
    #     if self.request.user.is_authenticated:
    #         print("There is a permission ")
    #         user = self.request.user
    #         recommended_quotes = QuoteModel.UserQuoteRecommendation.objects.filter(user=user).order_by('id') 
    #         # print(type(recommended_quotes))
    #     else:
    #     # Handle anonymous user case by showing popular quotes
    #         print("There is no permission ")
    #         recommended_quotes = QuoteModel.Quote.objects.annotate(num_likes=Count('quoteslikes')).order_by('-num_likes')[:100]
    #         print(recommended_quotes)
    #         # print(type(recommended_quotes))
                
    #     # recommended_quotes = Quote.objects.annotate(num_likes=Count('quoteslikes')).order_by('-num_likes')[:100]
    
    #     return recommended_quotes




    # Optionally, raise an error if you want to restrict this to authenticated users
    # def get(self, request, *args, **kwargs):
    #     if not request.user.is_authenticated:
    #         raise NotAuthenticated("You must be logged in to view recommendations.")
        

    #     return super().get(request, *args, **kwargs)

# # CRUD operations for Quotes
# class QuoteCreateAPIView(generics.CreateAPIView):
#     """
#     API view to create a new quote.
#     """
#     # queryset = QuoteModel.Quote.objects.all()
#     serializer_class = QuoteSerializer
#     permission_classes = [IsAuthenticated]
    
    
#     # def post(self, request):
#     #     form = QuoteForm(request.data)
#     #     if form.is_valid():
#     #         quote = form.save()
#     #         return Response({'message': 'Quote created successfully!'})
#     #     return Response({'error': 'Invalid data'}, status=400)    

#     def perform_create(self, serializer):
#         # Set the contributor as the current user
#         serializer.save(contributor=self.request.user)
        
        
#         text = self.request.data['text']
#         lang = self.request.data.get('lang', None)  # default to None if 'lang' is not provided

#         # Run your clean_text function
#         cleaned_text = clean_text(text, lang)

#         serializer.save(text=cleaned_text)      


class QuoteCreateAPIView(generics.CreateAPIView):
    serializer_class = QuoteSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        # Nettoyage
        text = self.request.data['text']
        lang = self.request.data.get('lang', None)
        cleaned_text = clean_text(text, lang)
        # author = self.request.data['author']        

        # Enrichissement
        insights = generate_response(cleaned_text)

        dimensions = {k: v for k, v in insights.items() if k != "categories"}
        categories = insights.get("categories", [])

        try:
            # Création de la quote
            with transaction.atomic():
                quote = serializer.save(
                    contributor=self.request.user,
                    text=cleaned_text,
                    dimensions=dimensions,
                  
                    lang=lang,
                    # author=author
                )

                # Associer les catégories
                if categories:
                    cat_objs = []
                    for cat_name in categories:
                        cat, _ = Category.objects.get_or_create(
                            title__iexact=cat_name.strip(),
                            defaults={"title": cat_name.strip()}
                        )
                        cat_objs.append(cat)

                    quote.categories.set(cat_objs)

        except QuoteDuplicateException as e:
            raise ValidationError({
                "detail": str(e),
                "existing_quote_id": e.quote_id,
                # "existing_author_id": e.author_id
            })

class QuoteUpdateAPIView(generics.UpdateAPIView):
    """
    API view to update an existing quote.
    """
    queryset = QuoteModel.Quote.objects.all()
    serializer_class = QuoteSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "id"
    http_method_names = ['put', 'patch']

    def get_queryset(self):
        # Users can only update quotes they contributed
        return QuoteModel.Quote.objects.filter(contributor=self.request.user)
    
    # def perform_update(self, serializer):
    #     # Optional logging
    #     # print("Updating quote:", serializer.validated_data)
    #     serializer.save()    
        
    # def update(self, request, *args, **kwargs):
    #     instance = self.get_object()
    #     serializer = self.get_serializer(instance, data=request.data, partial=True)

    #     if serializer.is_valid():
    #         serializer.save()
    #         # return Response({"message": "mobile number updated successfully"})

    #     else:
    #         return Response({"message": "failed", "details": serializer.errors})        
    
    # def perform_update(self, serializer):
    #     # text = self.request.data['text']
    #     # lang = self.request.data.get('lang', None)  # default to None if 'lang' is not provided
    #     # categories = self.request.data.get('categories', None) 
    #     # # Run your clean_text function
    #     # cleaned_text = clean_text(text, lang)

    #     serializer.save()          

class QuoteDeleteAPIView(generics.DestroyAPIView):
    """
    API view to delete a quote.
    """
    queryset = QuoteModel.Quote.objects.all()
    serializer_class = QuoteSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "id"

    def get_queryset(self):
        # Users can only delete quotes they contributed
        return QuoteModel.Quote.objects.filter(contributor=self.request.user)

# CRUD operations for Authors
class AuthorCreateAPIView(generics.CreateAPIView):
    """
    API view to create a new author.
    """
    queryset = AuthorModel.Author.objects.all()
    serializer_class = AuthorSerializer
    permission_classes = [IsAuthenticated]

class AuthorUpdateAPIView(generics.UpdateAPIView):
    """
    API view to update an existing author.
    """
    queryset = AuthorModel.Author.objects.all()
    serializer_class = AuthorSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "slug"

class AuthorDeleteAPIView(generics.DestroyAPIView):
    """
    API view to delete an author.
    """
    queryset = AuthorModel.Author.objects.all()
    serializer_class = AuthorSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "slug"
    
    
    


# class TemporaryImageUploadView(APIView):
#     def post(self, request):
#         image_data = request.data.get("image")
#         if not image_data:
#             return Response({"error": "No image provided"}, status=status.HTTP_400_BAD_REQUEST)

#         try:
#             format, imgstr = image_data.split(';base64,')
#             ext = format.split('/')[-1]
#             filename = f"{uuid4().hex}.{ext}"
#             save_dir = os.path.join(settings.MEDIA_ROOT, 'generated')
#             os.makedirs(save_dir, exist_ok=True)

#             file_path = os.path.join(save_dir, filename)
#             with open(file_path, "wb") as f:
#                 f.write(base64.b64decode(imgstr))

#             # Auto-delete after 5 min
#             def delete_later(path, delay=300):
#                 time.sleep(delay)
#                 if os.path.exists(path):
#                     os.remove(path)
#             threading.Thread(target=delete_later, args=(file_path,)).start()

#             image_url = request.build_absolute_uri(f"{settings.MEDIA_URL}generated/{filename}")
#             return Response({"image_url": image_url}, status=status.HTTP_201_CREATED)

#         except Exception as e:
#             return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
