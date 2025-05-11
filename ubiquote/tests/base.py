import pytest
from django.test import TestCase, Client
from django.db import transaction
from rest_framework.test import APIClient
from django.conf import settings
import uuid

class BaseTestCase(TestCase):
    """
    Base test class that handles both API and web app testing
    """
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.client = Client()
        cls.api_client = APIClient()
        
    def setUp(self):
        super().setUp()
        # Start a transaction for each test
        transaction.set_autocommit(False)
        self.transaction = transaction.atomic()
        self.transaction.__enter__()

    def tearDown(self):
        # Rollback the transaction after each test
        if hasattr(self, 'transaction'):
            self.transaction.__exit__(None, None, None)
        transaction.set_autocommit(True)
        super().tearDown()

    def get_unique_string(self, prefix=''):
        """Generate a unique string for testing"""
        return f"{prefix}_{uuid.uuid4().hex[:8]}"

    def create_test_user(self, **kwargs):
        """Create a test user with unique username and email"""
        from persons.users.models import User
        username = kwargs.get('username', self.get_unique_string('user'))
        email = kwargs.get('email', f"{username}@test.com")
        password = kwargs.get('password', 'testpass123')
        
        return User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

    def sync_api_web_slugs(self, api_obj, web_obj):
        """
        Synchronize slugs between API and web app objects
        Returns tuple of (api_slug, web_slug)
        """
        return (
            f"api_{self.get_unique_string()}",
            f"web_{self.get_unique_string()}"
        )

    def create_api_quote(self, **kwargs):
        """Create a quote through the API"""
        # Implementation depends on your API structure
        pass

    def create_web_quote(self, **kwargs):
        """Create a quote in the web app database"""
        from texts.quotes.models import Quote
        return Quote.objects.create(**kwargs) 