from rest_framework import serializers
from texts.quotes import models as mquotes
from persons.authors import models as mauthors
from persons.users import models as musers
from texts import models as tmodels

class ShortUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = musers.User
        fields = ["username", "id", "slug" ]
        
        
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = musers.User
        fields = "__all__"       


class TranslatedNameMixin:
    def get_translated_name(self, obj):
        # Fetch all translations for this author
        translations = mauthors.AuthorTranslation.objects.filter(author=obj)
        # Create a dictionary of language codes to translated names
        return {translation.language_code: translation.translated_name for translation in translations}


class ShortAuthorSerializer(TranslatedNameMixin, serializers.ModelSerializer):
    translated_name = serializers.SerializerMethodField()
    quote_count = serializers.SerializerMethodField()    

    class Meta:
        model = mauthors.Author
        fields = ["id", "slug", "fullname", "last_name", "translated_name", 'quote_count']
        
    def get_quote_count(self, obj):
        # This method will return the count of quotes related to this author
        return mquotes.Quote.objects.filter(author=obj).count()        

class AuthorSerializer(TranslatedNameMixin, serializers.ModelSerializer):
    translated_name = serializers.SerializerMethodField()

    class Meta:
        model = mauthors.Author
        fields = "__all__"  # This includes all fields from the model, plus the translated_name field



# Nested Category Serializer
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = tmodels.Category
        fields = "__all__"        
        # fields = ["id", "title"]  # Adjust the fields as needed        


class QuoteSerializer(serializers.ModelSerializer):
    
    # Nest the Author and Category serializers
    author = ShortAuthorSerializer()  # Nested author data
    categories = CategorySerializer(many=True, read_only=True)  # Nested categories data
    contributor = ShortUserSerializer()    
    
    # user = ShortUserSerializer()       
    
    # likes_count = serializers.IntegerField(source='likes.count', read_only=True)
    # has_user_liked = serializers.SerializerMethodField()    
    
    likes_count = serializers.IntegerField(source='likes.count', read_only=True)
    has_user_liked = serializers.SerializerMethodField()    
    
    class Meta:
        model = mquotes.Quote
        fields = "__all__"  
        # fields = ["id", "text", "author", "categories", "lang", "likes", "contributor", "date_created", "likes_count", "has_user_liked", "slug" ]
        
    
    def get_has_user_liked(self, obj):
        user = self.context['request'].user  # Access request from context
        if user.is_authenticated:
            return mquotes.QuotesLikes.objects.filter(user=user, quote=obj).exists()
        return False

    def get_likes_count(self, obj):
        return obj.likes.count()
    
    


        
class ShortQuoteSerializer(serializers.ModelSerializer):
    author = ShortAuthorSerializer() 
    contributor = ShortUserSerializer()   
    categories = CategorySerializer(many=True, read_only=True)  # Nested categories data
 
    likes_count = serializers.IntegerField(source='likes.count', read_only=True)
    has_user_liked = serializers.SerializerMethodField() 

    class Meta:
        model = mquotes.Quote
        fields = ["id", "text", "author", "categories", "lang", "likes", "contributor", "date_created", "likes_count", "has_user_liked", "slug" ]

        
    def get_has_user_liked(self, obj):
        user = self.context['request'].user  # Access request from context
        if user.is_authenticated:
            return mquotes.QuotesLikes.objects.filter(user=user, quote=obj).exists()
        return False

    

class ShortQuotesLikesSerializer(serializers.ModelSerializer):
    user = ShortUserSerializer()  # Nested user data
    quote = ShortQuoteSerializer()  # Nested quote data

    class Meta:
        model = mquotes.QuotesLikes
        fields = "__all__"  
        

        
class QuotesLikesSerializer(serializers.ModelSerializer):
    class Meta:
        model = mquotes.QuotesLikes
        fields = ['user', 'quote']