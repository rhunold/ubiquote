import pytest
from tests.base import BaseTestCase
from persons.users.models import User
from persons.authors.models import Author
from texts.quotes.models import Quote, QuotesLikes
from django.urls import reverse
from django.test import override_settings
from django.db import transaction

"""
@pytest.mark.django_db(transaction=True)
class TestQuotesAndLikes(BaseTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        try:
            cls.anonymous_author = Author.objects.get(nickname="Anonymous")
        except Author.DoesNotExist:
            cls.anonymous_author = Author.objects.create(
                nickname="Anonymous",
                slug="anonymous"
            )

    def setUp(self):
        super().setUp()
        self.user = User.objects.create_user(
            username=self.get_unique_string("user"),
            password="testpass123"
        )
        
        self.test_author = Author.objects.create(
            nickname=self.get_unique_string("author"),
            slug=self.get_unique_string("author-slug")
        )
        
        self.test_quote = Quote.objects.create(
            text=self.get_unique_string("quote-text"),
            author=self.test_author,
            contributor=self.user,
            slug=self.get_unique_string("quote-slug")
        )

    def tearDown(self):
        Quote.objects.all().delete()
        Author.objects.exclude(nickname="Anonymous").delete()
        User.objects.all().delete()
        super().tearDown()

    def test_1_user_create(self):
        username = self.get_unique_string("new-user")
        test_user = User.objects.create_user(
            username=username,
            password="new-password"
        )
        test_user.set_password("new-password")
        test_user.save()
        
        assert test_user.check_password("new-password") is True
        assert User.objects.filter(username=username).exists()

    def test_2_user_create_quote(self):
        quote = Quote.objects.create(
            text=self.get_unique_string("new-quote"),
            author=self.test_author,
            contributor=self.user,
            slug=self.get_unique_string("new-quote-slug")
        )
        assert quote.pk is not None
        assert Quote.objects.filter(pk=quote.pk).exists()

    def test_3_view_home(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('home'))
        assert response.status_code == 200

    def test_4_view_quotes_list(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('quotes:quotes-list'))
        assert response.status_code == 200

    def test_5_view_quote_detail(self):
        self.client.force_login(self.user)
        response = self.client.get(
            reverse('quotes:quote-detail', kwargs={'slug': self.test_quote.slug})
        )
        assert response.status_code == 200
        assert self.test_quote.text in response.content.decode()

    def test_6_quote_like_operations(self):
        quote_like = QuotesLikes.objects.create(
            quote=self.test_quote,
            user=self.user
        )
        assert quote_like.pk is not None

        retrieved = QuotesLikes.objects.get(pk=quote_like.pk)
        assert retrieved == quote_like

        quote_like.delete()
        with pytest.raises(QuotesLikes.DoesNotExist):
            QuotesLikes.objects.get(pk=quote_like.pk)

@pytest.mark.django_db
def test_new_user_factory(db, user_factory):
    user = user_factory.create(
        username=f"test-user-{User.objects.count() + 1}"
    )
    assert user.pk is not None
    user.delete()

@pytest.mark.django_db
def test_new_quote_factory(db, quote_factory):
    quote = quote_factory.create(
        text=f"Test quote {Quote.objects.count() + 1}",
        slug=f"test-quote-{Quote.objects.count() + 1}"
    )
    assert quote.pk is not None
    quote.delete()
"""