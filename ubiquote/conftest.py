import pytest
from django.test import Client

from persons.users.models import User
from persons.authors.models import Author
from texts.quotes.models import Quote, QuotesLikes


from django.conf import settings
import os
from dotenv import load_dotenv

# Load environments variables
load_dotenv()

pytestmark = pytest.mark.django_db

@pytest.fixture()
def client():
    """
    Create a Django test client instance.
    """
    return Client()

@pytest.fixture(scope='session')
def django_db_setup():
    settings.DATABASES['default'] = {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': os.environ.get('DATABASES_NAME'),
        'USER': os.environ.get('DATABASES_USER'),
        'PASSWORD': os.environ.get('DATABASES_PASSWORD'),
        'HOST': os.environ.get('DATABASES_HOST'),
        'PORT': os.environ.get('DATABASES_PORT'),
        'ATOMIC_REQUESTS': True,  # Ensure this line is present and set to True        
 
}
    
    
@pytest.fixture
def user():
    user_instance, created = User.objects.get_or_create(username='test2', email='test2@gmail.com', password='test2')
    return user_instance


@pytest.fixture
def quote(user):
    anonyme_author, created = Author.objects.get_or_create(nickname="Anonyme")    
    # Create a test quote
    return Quote.objects.create(
        text="Test quote",
        author=anonyme_author,
        contributor=user  # Now user is a User instance, not a tuple
    )