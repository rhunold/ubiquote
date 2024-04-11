from django.db.models import Count
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from .models import Quote, QuotesLikes
from persons.users.models import User

import time
from django.db.models import Count, F  
from django.core.cache import cache  # Import Django cache module

# from django_pgvector.expressions import VectorField as PGVectorField


# class RecommendationService:
#     @staticmethod
#     def recommend_quotes(user_id, num_recommendations=10):
#         start_time = time.time()  # Record start time
        
#         num_liked_quotes = QuotesLikes.objects.filter(user_id=user_id).count()
        
#         if num_liked_quotes != 0:
#             liked_quotes_texts = QuotesLikes.objects.filter(user_id=user_id).values_list('quote__text', flat=True)
            
#             # Get liked quotes TF-IDF vectors
#             liked_quotes_vectors = Quote.objects.filter(text__in=liked_quotes_texts).annotate(
#                 tfidf_vector=PGVectorField('tfidf_vector')
#             ).values_list('tfidf_vector', flat=True)
            
#             # Compute similarity between liked quotes and all quotes
#             # Use PGVectorField for all_quotes_tfidf
#             all_quotes_tfidf = Quote.objects.exclude(text__in=liked_quotes_texts).annotate(
#                 tfidf_vector=PGVectorField('tfidf_vector')
#             ).values_list('tfidf_vector', flat=True)
#             similarity_matrix = cosine_similarity(liked_quotes_vectors, all_quotes_tfidf)
            
#             # Get indices of top similar quotes
#             top_indices = similarity_matrix.argsort(axis=1)[:, -num_recommendations:]
            
#             # Get top recommended quotes
#             recommended_quotes_ids = Quote.objects.exclude(text__in=liked_quotes_texts).values_list('id', flat=True)[top_indices.ravel()]
#             recommended_quotes = Quote.objects.filter(id__in=recommended_quotes_ids)
#         else:
#             # Generate recommendations from top liked quotes
#             top_quotes = Quote.objects.annotate(num_likes=Count('quoteslikes')).order_by('-num_likes', 'id')[:num_recommendations]
#             recommended_quotes = top_quotes
        
#         end_time = time.time()  # Record end time
#         execution_time = end_time - start_time
#         print(f"Execution time: {execution_time:.4f} seconds")  # Display execution time

#         return recommended_quotes


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
    def recommend_quotes(user_id, num_recommendations=10):
        
        start_time = time.time()  # Record start time
        
        num_liked_quotes = QuotesLikes.objects.filter(user_id=user_id).count()
        
        if num_liked_quotes != 0:
            liked_quotes_texts = QuotesLikes.objects.filter(user_id=user_id).values_list('quote__text', flat=True)

            # Compute TF-IDF vectors for liked quotes
            vectorizer = RecommendationService.get_vectorizer()
            liked_quotes_tfidf = vectorizer.fit_transform(liked_quotes_texts)
            
            # Get all quotes texts excluding the ones liked by the user
            excluded_quotes_texts = QuotesLikes.objects.filter(user_id=user_id).values_list('quote__text', flat=True)
            all_quotes_texts = Quote.objects.exclude(text__in=excluded_quotes_texts).values_list('text', flat=True)
            

            # Compute similarity between liked quotes and all quotes
            # all_quotes_texts = Quote.objects.exclude(quoteslikes__user_id=user_id).values_list('text', flat=True)
            all_quotes_tfidf = vectorizer.transform(all_quotes_texts)
            similarity_matrix = cosine_similarity(liked_quotes_tfidf, all_quotes_tfidf)

            # Get indices of top similar quotes
            top_indices = similarity_matrix.argsort(axis=1)[:, -num_recommendations:]

            # Get top recommended quotes
            recommended_quotes_ids = [all_quotes_texts[i.item()] for i in top_indices.ravel()]
            recommended_quotes = Quote.objects.filter(text__in=recommended_quotes_ids)            
        else:
        # # If the favorite quotes = 0
        # if not liked_quotes_texts:
            # If the user has not liked any quotes, generate recommendations from top 100 most liked quotes
            liked_quotes_texts = Quote.objects.annotate(num_likes=Count('quoteslikes')).order_by('-num_likes', 'id')[:10]
            recommended_quotes_list = [quote.text for quote in liked_quotes_texts]
            recommended_quotes = Quote.objects.filter(text__in=recommended_quotes_list)            
            # print(recommended_quotes)
            return recommended_quotes
        
        
        end_time = time.time()  # Record end time
        execution_time = end_time - start_time
        print(f"Execution time: {execution_time:.4f} seconds")  # Display execution time

        return recommended_quotes
    
