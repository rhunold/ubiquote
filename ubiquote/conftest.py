# import pytest

# @pytest.fixture
# def sample_quote():
#     return "Life is short."



import pytest
from django.test import Client
from pytest_factoryboy import register
from texts.quotes.tests.factories import UserFactory, QuoteFactory

from persons.users.models import User
from persons.authors.models import Author
from texts.quotes.models import Quote, QuotesLikes

from django.conf import settings
import os
from dotenv import load_dotenv


load_dotenv()

register(UserFactory) # user_factory
register(QuoteFactory)

pytestmark = pytest.mark.django_db

@pytest.fixture()
def client():
    """
    Create a Django test client instance.
    """
    return Client()

@pytest.fixture
def new_user_factory(db):
    def create_app_user(
            username: str = 'test2',
            email: str = 'test2@gmail.com',
            password: str = None,
            is_staff: str = False,
            is_superuser: str = False,            
            is_active: str = True
            ):
        user = User.objects.create_user(username=username,
                                        email=email,
                                        password=password,
                                        is_staff=is_staff,
                                        is_superuser=is_superuser,
                                        is_active=is_active)
        return user
    return create_app_user

@pytest.fixture
def user(db, new_user_factory):
    return new_user_factory('test2', 'test2@gmail.com', 'test2')

@pytest.fixture
def admin(db, new_user_factory):
    return new_user_factory('admin2', 'admin2@gmail.com', 'admin2', is_superuser="True")

@pytest.fixture
def quote(user):
    anonyme_author, created = Author.objects.get_or_create(nickname="Anonyme")    
    # Create a test quote
    return Quote.objects.create(
        text="Test quote",
        author=anonyme_author,
        contributor=user,
    )