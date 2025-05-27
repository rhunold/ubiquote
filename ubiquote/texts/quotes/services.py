from django.db.models import Count
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from .models import Quote, QuotesLikes, UserQuoteRecommendation
from persons.users.models import User

from django.shortcuts import get_object_or_404

import time
from django.db.models import Count, F  
from django.core.cache import cache  # Import Django cache module

from django.core.paginator import Paginator

import numpy as np

from django.db.models import Count
from django.utils import timezone
import random

class RecommendationService:
    vectorizer = None  # Static variable to hold the vectorizer instance
    cached_num_liked_quotes = None
    
    
    
    
    # Optimization on TF-IDF computation / avoid redundant fit-transform operations
    @staticmethod
    def get_vectorizer():
        if RecommendationService.vectorizer is None:
            RecommendationService.vectorizer = TfidfVectorizer()
        return RecommendationService.vectorizer 
    
    

    @staticmethod
    def recommend_quotes_for_liked_quote(quote, user, num_recommendations=10):
        # Get the text of the liked quote
        liked_quote_text = quote.text

        # Get the lang of the liked quote
        liked_quote_lang = quote.lang 
        
        

        # Compute TF-IDF vector for the liked quote
        vectorizer = RecommendationService.get_vectorizer()
        liked_quote_tfidf = vectorizer.fit_transform([liked_quote_text])

        # Get all quotes excluding the liked one
        # excluded_quote_texts = [liked_quote_text]
        excluded_quote_texts = QuotesLikes.objects.filter(user_id=user).values_list('quote__text', flat=True)
        
        
        # all_quotes_texts = Quote.objects.exclude(text__in=excluded_quote_texts).values_list('text', flat=True)
        all_quotes_texts = Quote.objects.filter(lang=liked_quote_lang).exclude(text__in=excluded_quote_texts).values_list('text', flat=True)
        

        # Compute TF-IDF vectors for all quotes
        all_quotes_tfidf = vectorizer.transform(all_quotes_texts)

        # Compute similarity between the liked quote and all quotes
        similarity_matrix = cosine_similarity(liked_quote_tfidf, all_quotes_tfidf)

        # Get the indices of the most similar quotes
        top_indices = similarity_matrix.argsort(axis=1)[:, -num_recommendations:]

        # Convert numpy int64 to Python integers and get the corresponding texts
        recommended_quotes_texts = [all_quotes_texts[int(i)] for i in top_indices.flatten()]

        # Get the quote objects corresponding to the recommended texts
        recommended_quotes = Quote.objects.filter(text__in=recommended_quotes_texts)

        # (Optional) Save the recommendations in the database for future use
        # user = User.objects.get(id=user_id)
        for quote in recommended_quotes:
            UserQuoteRecommendation.objects.create(user=user, quote=quote)

        return recommended_quotes    
    
    
    
    # @staticmethod
    # def recommend_quotes(user_id, num_recommendations=10, request=None):
    #     # Check if user_id is valid
    #     if user_id is None:
    #         quotes = Quote.objects.annotate(num_likes=Count('quoteslikes')).order_by('-num_likes')[:num_recommendations]
    #     else:
            
    #         user = User.objects.get(id=user_id)
        
    #         # # Check if there are existing recommendations
    #         # existing_recommendations = UserQuoteRecommendation.objects.filter(user=user)

    #         # if existing_recommendations.exists():
    #         #     return existing_recommendations
                
            
            
    #         num_liked_quotes = QuotesLikes.objects.filter(user_id=user_id).count()  
            
    #         if num_liked_quotes != 0:
    #             liked_quotes_texts = QuotesLikes.objects.filter(user_id=user_id).values_list('quote__text', flat=True)

    #             # Compute TF-IDF vectors for liked quotes
    #             vectorizer = RecommendationService.get_vectorizer()
                
    #             # Fit only if the user has new liked quotes (cache num_liked_quotes)
    #             if RecommendationService.cached_num_liked_quotes != num_liked_quotes:
    #                 liked_quotes_tfidf = vectorizer.fit_transform(liked_quotes_texts)
    #                 RecommendationService.cached_num_liked_quotes = num_liked_quotes
    #             else:
    #                 liked_quotes_tfidf = vectorizer.transform(liked_quotes_texts)            
                
    #             # Get all quotes texts excluding the ones liked by the user
    #             excluded_quotes_texts = QuotesLikes.objects.filter(user_id=user_id).values_list('quote__text', flat=True)
    #             all_quotes_texts = Quote.objects.exclude(text__in=excluded_quotes_texts).values_list('text', flat=True)

    #             # Compute similarity between liked quotes and all quotes
    #             all_quotes_tfidf = vectorizer.transform(all_quotes_texts)
    #             similarity_matrix = cosine_similarity(liked_quotes_tfidf, all_quotes_tfidf)

    #             # Get indices of top similar quotes
    #             top_indices = similarity_matrix.argsort(axis=1)[:, -num_recommendations:]

    #             # **Fix: Convert numpy int64 to Python integers**
    #             recommended_quotes_texts = [all_quotes_texts[int(i)] for i in top_indices.flatten()]
    #             quotes = Quote.objects.filter(text__in=recommended_quotes_texts)
                
    #             # # Once recommendations are generated, save them in the database
    #             # quotes = Quote.objects.annotate(num_likes=Count('quoteslikes')).order_by('-num_likes')[:num_recommendations]
                        
    #             # # Save the recommendations
    #             # for quote in quotes:
    #             #     UserQuoteRecommendation.objects.create(user=user, quote=quote, created_at=timezone.now())
                        
                

    #         else:
    #             # If the user has not liked any quotes, generate recommendations from top 100 most liked quotes
    #             quotes = Quote.objects.annotate(num_likes=Count('quoteslikes')).order_by('-num_likes')[:100]

    #     # # If there's a request, randomize for a new session
    #     # if request is not None:
    #     #     session = request.session
    #     #     if not session.get('randomized_homepage', False):
    #     #         # Randomize only once per session
    #     #         quotes = list(quotes)  # Convert QuerySet to list to allow shuffling
    #     #         random.shuffle(quotes)
    #     #         session['randomized_homepage'] = True  # Mark session as randomized
    #     #         request.session.save()  # Ensure session is saved

    #     return quotes  # Return the limited number of quotes








# class RecommendationService:
#     vectorizer = None  # Static variable to hold the vectorizer instance
#     cached_num_liked_quotes = None
    
#     # Optimization on TF-IDF computation / avoid redundant fit-transform operations
#     @staticmethod
#     def get_vectorizer():
#         if RecommendationService.vectorizer is None:
#             RecommendationService.vectorizer = TfidfVectorizer()
#         return RecommendationService.vectorizer 
    
#     @staticmethod
#     def recommend_quotes(user_id, num_recommendations=10):
#         # start_time = time.time()  # Record start time
        
#         # Check if user_id is valid
#         if user_id is None:
#             return Quote.objects.annotate(num_likes=Count('quoteslikes')).order_by('-num_likes')[:num_recommendations]
        
        
#         # user = get_object_or_404(User, id=user_id)
        
#         num_liked_quotes = QuotesLikes.objects.filter(user_id=user_id).count()  
        
#         if num_liked_quotes != 0:
#             liked_quotes_texts = QuotesLikes.objects.filter(user_id=user_id).values_list('quote__text', flat=True)

#             # Compute TF-IDF vectors for liked quotes
#             vectorizer = RecommendationService.get_vectorizer()
            
#             # Fit only if the user has new liked quotes (cache num_liked_quotes)
#             if RecommendationService.cached_num_liked_quotes != num_liked_quotes:
#                 liked_quotes_tfidf = vectorizer.fit_transform(liked_quotes_texts)
#                 RecommendationService.cached_num_liked_quotes = num_liked_quotes
#             else:
#                 liked_quotes_tfidf = vectorizer.transform(liked_quotes_texts)            
            
#             # Get all quotes texts excluding the ones liked by the user
#             excluded_quotes_texts = QuotesLikes.objects.filter(user_id=user_id).values_list('quote__text', flat=True)
#             all_quotes_texts = Quote.objects.exclude(text__in=excluded_quotes_texts).values_list('text', flat=True)

#             # Compute similarity between liked quotes and all quotes
#             all_quotes_tfidf = vectorizer.transform(all_quotes_texts)
#             similarity_matrix = cosine_similarity(liked_quotes_tfidf, all_quotes_tfidf)

#             # Get indices of top similar quotes
#             top_indices = similarity_matrix.argsort(axis=1)[:, -num_recommendations:]

#             # **Fix: Convert numpy int64 to Python integers**
#             recommended_quotes_texts = [all_quotes_texts[int(i)] for i in top_indices.flatten()]
#             recommended_quotes = Quote.objects.filter(text__in=recommended_quotes_texts)
#             # print("the user has liked before,")            
#             # print(type(recommended_quotes))
            

        
#         else:
#             # If the user has not liked any quotes, generate recommendations from top 100 most liked quotes
#             recommended_quotes = Quote.objects.annotate(num_likes=Count('quoteslikes')).order_by('-num_likes')[:100]

        
#         # end_time = time.time()  # Record end time
#         # execution_time = end_time - start_time
#         # print(f"Execution time: {execution_time:.4f} seconds")  # Display execution time

#         return recommended_quotes
