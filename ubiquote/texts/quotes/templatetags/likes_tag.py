# from django import template

print("test likes_tag.py")

# register = template.Library()

# @register.filter
# def has_user_liked(liked_quotes, quote_id_or_bool):

#     # if isinstance(liked_quotes, list):
#     #     # Case for ListView: liked_quotes is a dictionary
#     #     liked_quotes = liked_quotes.get(quote_id_or_bool, False)
#     #     print("test List")        
#     #     return liked_quotes
#     # else:
#     #     # Case for DetailView: liked_quotes is a boolean
#     #     print("test Detail")
#     #     return liked_quotes        
        
#     #     # return liked_quotes.get(quote_id, False)    


#     if isinstance(liked_quotes, dict):
#         # Case for ListView: liked_quotes is a dictionary
#         return liked_quotes.get(quote_id_or_bool, False)
#     elif isinstance(liked_quotes, bool):
#         # Case for DetailView: liked_quotes is a boolean
#         return liked_quotes
#     else:
#         # Handle unexpected data type gracefully
#         return False
    
    
# # @register.filter
# # def has_user_liked(liked_quotes, quote_id):
# #     return liked_quotes.get(quote_id, False)    