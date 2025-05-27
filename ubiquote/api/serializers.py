from rest_framework import serializers
from django.utils.translation import get_language
from texts.quotes import models as mquotes
from persons.authors import models as mauthors
from persons.users import models as musers
from texts import models as tmodels

from texts.quotes.utils import QuoteDuplicateException

class ShortUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = musers.User
        fields = ["username", "id", "slug" ]
        
        
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = musers.User
        # fields = "__all__"       
        fields = ["id", "username", "slug", "email", "avatar", "sex", "nationality", "twitter_url"]        


class TranslatedNameMixin:
    def get_translated_name(self, obj):
        # Fetch all translations for this author
        translations = mauthors.AuthorTranslation.objects.filter(author=obj)
        # Create a dictionary of language codes to translated names
        return {translation.language_code: translation.translated_name for translation in translations}


# class TranslatedCategoryMixin:
#     def get_translated_data(self, obj):
#         translations = tmodels.CategoryTranslation.objects.filter(category=obj)
#         return {
#             translation.language_code: {
#                 "title": translation.translated_title,
#                 "text": translation.translated_text
#             }
#             for translation in translations
#         }

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
    quote_count = serializers.SerializerMethodField()

    class Meta:
        model = mauthors.Author
        fields = ["id", "slug", "fullname", "last_name", "first_name", "translated_name",
                # "birth_date", "death_date", "nationality", "avatar", "sex", 
                # "occupation", "biography", 
                 "quote_count", ]
        read_only_fields = ["id", "slug"]

    def get_quote_count(self, obj):
        return mquotes.Quote.objects.filter(author=obj).count()



# Nested Category Serializer

# class CategorySerializer(TranslatedCategoryMixin, serializers.ModelSerializer):
#     translated_title = serializers.SerializerMethodField()
#     quotes_count = serializers.IntegerField(read_only=True)

#     class Meta:
#         model = tmodels.Category
#         fields = ['id', 'slug', 'translated_title', 'quotes_count']  # or add others like 'text' if needed

#     def get_translated_title(self, obj):
#         lang = get_language()
#         translation = obj.translations.filter(lang=lang).first()
#         return translation.title if translation else obj.title


class CategorySerializer(serializers.ModelSerializer):
    # quotes_count = serializers.SerializerMethodField()    
    quotes_count = serializers.IntegerField(read_only=True)    
    class Meta:
        model = tmodels.Category
        fields = "__all__"     
 
 
        # fields = ["id", "title"]  # Adjust the fields as needed  
    # def get_quotes_count(self, obj):
    #     return obj.quotes.count()       
    
    # def get_quotes_count(self, obj):
    #     return mquotes.Quote.objects.filter(author=obj).count()           


class QuoteSerializer(serializers.ModelSerializer):
    author = ShortAuthorSerializer(read_only=True)  # Nested author data for reading
    author_id = serializers.PrimaryKeyRelatedField(
        queryset=mauthors.Author.objects.all(),
        write_only=True,
        source='author'
    )
    categories = CategorySerializer(many=True, read_only=True)  # Nested categories data for reading
    category_ids = serializers.PrimaryKeyRelatedField(
        queryset=tmodels.Category.objects.all(),
        write_only=True,
        source='categories',
        many=True,
        required=False
    )
    
    
    contributor = ShortUserSerializer(read_only=True)
    likes_count = serializers.IntegerField(source='likes.count', read_only=True)
    has_user_liked = serializers.SerializerMethodField()
    
    dimensions = serializers.JSONField(read_only=True)  

    class Meta:
        model = mquotes.Quote
        fields = ["id", "text", "author", "author_id", "categories", "category_ids", 
                 "lang", "likes", "contributor", "date_created", "likes_count", 
                 "has_user_liked", "slug", "dimensions"]
        read_only_fields = ["id", "likes", "has_user_liked"] # "slug", "date_created"
        
        

    def get_has_user_liked(self, obj):
        user = self.context['request'].user if 'request' in self.context else None
        if user and user.is_authenticated:
            return mquotes.QuotesLikes.objects.filter(user=user, quote=obj).exists()
        return False

    # def get_likes_count(self, obj):
    #     return obj.likes.count()
    
    def create(self, validated_data):
        try:
            return super().create(validated_data)
        except QuoteDuplicateException as e:
            raise serializers.ValidationError({
                "non_field_errors": [str(e)]
            })
                
    def update(self, instance, validated_data):
        print("initial_data:", self.initial_data)
        print("validated_data:", validated_data)

        categories = validated_data.pop('categories', None)
        # dimensions = validated_data.pop('dimensions', None)
           
        print("Categories to update:", categories)
        
        # Update other fields normally
        instance = super().update(instance, validated_data)
        
        if categories is not None:
            instance.categories.set(categories)  # replaces old ones
            # OR use clear/add if you have extra logic in your through model

        # if dimensions:
        #     instance.dimensions.set(dimensions) 
        #     print(dimensions)
            
        return instance            


    # def update(self, validated_data):
    #     try:
    #         return super().update(validated_data)
    #     except QuoteDuplicateException as e:
    #         raise serializers.ValidationError({
    #             "non_field_errors": [str(e)]
    #         })                


class QuoteRecommandSerializer(serializers.ModelSerializer):
    pass
    
    # # user = ShortUserSerializer()   
    
    # author = serializers.CharField(source='quote.author', read_only=True)  # Access author via related quote

    # categories = serializers.CharField(source='quote.categories', read_only=True)  # Access categories via related quote
    # contributor = serializers.CharField(source='quote.contributor', read_only=True)  # Access categories via related quote
    
    # likes_count = serializers.IntegerField(source='likes.count', read_only=True)
    # has_user_liked = serializers.SerializerMethodField()    
        

    # class Meta:
    #     model = mquotes.UserQuoteRecommendation  # or Quote if directly serializing quotes
    #     fields = ['quote', 'author', 'contributor', 'has_user_liked', 'likes_count', 'categories', ]  # Adjust as per your fields
    #     # fields = "__all__"     
    #     print(fields)     

    # # def get_user(self, obj):
    # #     return obj.user

    # def get_author(self, obj):
    #     return obj.quote.author  # Make sure it retrieves the author from the related Quote model
    
    # def get_contributor(self, obj):
    #     return obj.quote.contributor  # Make sure it retrieves the author from the related Quote model
        

    # def get_has_user_liked(self, obj):
    #     user = self.context['request'].user  # Access request from context
    #     if user.is_authenticated:
    #         return mquotes.QuotesLikes.objects.filter(user=user, quote=obj).exists()
    #     return False

    # def get_likes_count(self, obj):
    #     return obj.likes.count()    
    


        
class ShortQuoteSerializer(serializers.ModelSerializer):
    author = ShortAuthorSerializer() 
    contributor = ShortUserSerializer()   
    categories = CategorySerializer(many=True, read_only=True)  # Nested categories data
    
    dimensions = serializers.JSONField(read_only=True)        
 
    likes_count = serializers.IntegerField(source='likes.count', read_only=True)
    has_user_liked = serializers.SerializerMethodField() 

    class Meta:
        model = mquotes.Quote
        fields = ["id", "text", "author", "categories", "lang", "likes", "contributor", "date_created", "likes_count", "has_user_liked", "slug" , "dimensions"]

        
    def get_has_user_liked(self, obj):
        user = self.context['request'].user  # Access request from context
        if user.is_authenticated:
            return mquotes.QuotesLikes.objects.filter(user=user, quote=obj).exists()
        return False

    def get_likes_count(self, obj):
        return obj.likes.count()
    

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