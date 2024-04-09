from django.db.models import Count
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from .models import Quote, QuotesLikes



class RecommendationService:
    @staticmethod
    def recommend_quotes(user_id, num_recommendations=100):

        
        liked_quotes_texts = QuotesLikes.objects.filter(user_id=user_id).values_list('quote__text', flat=True)
        
        
        # If the favorite quotes = 0
        if not liked_quotes_texts:
            # If the user has not liked any quotes, generate recommendations from top 100 most liked quotes
            liked_quotes_texts = Quote.objects.annotate(num_likes=Count('quoteslikes')).order_by('-num_likes', 'id')[:100]
            recommended_quotes = [quote.text for quote in liked_quotes_texts]
            # print(recommended_quotes)
            return liked_quotes_texts
        
        # Compute TF-IDF vectors for liked quotes
        vectorizer = TfidfVectorizer()
        liked_quotes_tfidf = vectorizer.fit_transform(liked_quotes_texts)

        # Compute similarity between liked quotes and all quotes
        all_quotes_texts = Quote.objects.exclude(quoteslikes__user_id=user_id).values_list('text', flat=True)
        all_quotes_tfidf = vectorizer.transform(all_quotes_texts)
        similarity_matrix = cosine_similarity(liked_quotes_tfidf, all_quotes_tfidf)

        # Get indices of top similar quotes
        top_indices = similarity_matrix.argsort(axis=1)[:, -num_recommendations:]

        # Get top recommended quotes
        recommended_quotes_ids = [all_quotes_texts[i.item()] for i in top_indices.ravel()]
        recommended_quotes = Quote.objects.filter(text__in=recommended_quotes_ids)
        return recommended_quotes
