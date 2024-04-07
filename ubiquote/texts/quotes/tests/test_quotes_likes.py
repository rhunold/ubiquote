import pytest

from persons.users.models import User
from persons.authors.models import Author
from texts.quotes.models import Quote, QuotesLikes

from django.db import connection

# Test database 
def test_user_notnull(db):
    assert User.objects.count() != 0

# A mettre dans le fichier test de l'app user
def test_user_create(db):
    count_before = User.objects.count() 
    user = User.objects.create_user(username='test2', email='test2@gmail.com', password='test2')
    assert user.username is "test2"    
    user.set_password("new-password")
    assert user.check_password("new-password") is True
    assert User.objects.count() != count_before
    


def test_user_create_quote(db, user):
    # user = User.objects.create_user(username='test2', email='test2@gmail.com', password='test2')
    anonyme_author, created = Author.objects.get_or_create(nickname="Anonyme")
    # author = Author("Anonyme")
    
    # Créer une citation associée à l'utilisateur
    quote = Quote.objects.create(
        text="Contenu de la citation",
        author=anonyme_author,  # Utilisez l'utilisateur créé comme auteur de la citation
    )
    
    # Vérifier le nombre total de citations dans la base de données (+1)
    assert Quote.objects.count() == 11771 + 1


def test_view_home(db, client):
    response = client.get('/en/')  # Make a GET request to the specified URL
    assert response.status_code == 200  # Assert that the response status code is 200 OK
    assert 'Welcome in Extraquote' in response.content.decode()  # Assert that the response contains expected content


def test_view_en_quotes(db, client, user):
    # Authenticate the user using force_login
    client.force_login(user)
        
    # Make a GET request to the specified URL
    response = client.get('/en/quotes/') 
    
    assert response.status_code == 200  # Assert that the response status code is 200 OK
    assert 'quotes available in the database' in response.content.decode()  # Assert that the response contains expected content


def test_view_en_quote(client, db, user, quote):
    client.force_login(user)    
    response = client.get(f'/en/quote/{quote.slug}')
    assert quote.text in response.content.decode()
    assert response.status_code == 200      


def test_create_quote_like(db, user, quote):
    # Test creating a new quote like      
    quote_like, created = QuotesLikes.objects.get_or_create(quote=quote, user=user)       
    assert quote_like.id is not None

def test_get_quote_like(db, user, quote):
    # Test retrieving a quote like from the database
    quote_like = QuotesLikes.objects.create(quote=quote, user=user)
    retrieved_quote_like = QuotesLikes.objects.get(id=quote_like.id)
    assert quote_like.id == retrieved_quote_like.id


def test_delete_quote_like(db, user, quote):
    quote_like = QuotesLikes.objects.create(quote=quote, user=user)
    quote_like_id = quote_like.id
    quote_like.delete()
    with pytest.raises(QuotesLikes.DoesNotExist): # If the expected exception is raised, the test passes.
        QuotesLikes.objects.get(id=quote_like_id)


## testings with  factory boy

def test_new_user_factory(db, user_factory):
    count_before = User.objects.count()  
        
    # user = user_factory.build() # Just build 
    user = user_factory.create() # save to DB (delete at end of test) / need DB access with django_db
    # print(user.first_name)

    assert User.objects.count() != count_before   
    assert True
    
def test_new_quote_factory(db, quote_factory):
    # user = user_factory.build() # Just build 
    quote = quote_factory.create() # save to DB (delete at end of test) / need DB access with django_db
    # print(quote.text)
    assert True    

# def test_new_quotes_factory(db, quote_factory):
#     # user = user_factory.build() # Just build 
#     quote1 = quote_factory.build()
#     quote2 = quote_factory.build()    
#     print(quote1.text)
#     print(quote2.text)
#     assert True    

