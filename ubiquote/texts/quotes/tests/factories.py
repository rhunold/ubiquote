import factory
from factory.django import DjangoModelFactory
from faker import Faker
from persons.users.models import User
from persons.authors.models import Author
from texts.quotes.models import Quote
import uuid

from autoslug import AutoSlugField


# https://faker.readthedocs.io/en/stable/providers/faker.providers.person.html


class UserFactory(DjangoModelFactory):
    class Meta:
        model = User
        django_get_or_create = ('username',)

    username = factory.Sequence(lambda n: f'testuser_{n}_{uuid.uuid4().hex[:8]}')
    email = factory.LazyAttribute(lambda obj: f'{obj.username}@example.com')
    password = factory.PostGenerationMethodCall('set_password', 'testpass123')


class AuthorFactory(DjangoModelFactory):
    class Meta:
        model = Author
        django_get_or_create = ('nickname',)

    nickname = factory.Sequence(lambda n: f'author_{n}_{uuid.uuid4().hex[:8]}')
    slug = factory.LazyAttribute(lambda obj: f'author-{obj.nickname.lower()}')


class QuoteFactory(DjangoModelFactory):
    class Meta:
        model = Quote
        django_get_or_create = ('slug',)

    text = factory.Sequence(lambda n: f'Test quote {n} {uuid.uuid4().hex[:8]}')
    author = factory.SubFactory(AuthorFactory)
    contributor = factory.SubFactory(UserFactory)
    slug = factory.LazyAttribute(lambda obj: f'quote-{uuid.uuid4().hex[:8]}')

    @factory.post_generation
    def sync_with_api(self, create, extracted, **kwargs):
        """
        Ensure the quote has matching records in both databases
        """
        if not create:
            return
            
        # Here you would typically create/sync the API version
        # Implementation depends on your API structure
        pass

