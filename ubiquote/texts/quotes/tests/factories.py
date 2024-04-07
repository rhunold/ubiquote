import factory
from faker import Faker
fake = Faker()
from persons.users.models import User
from texts.quotes.models import Quote

from autoslug import AutoSlugField


# https://faker.readthedocs.io/en/stable/providers/faker.providers.person.html


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User
        # database = 'my_db2'        
    
    email = fake.email()    
    username = fake.name()
    last_name = fake.last_name() # 'name'
    first_name = fake.first_name()  
    is_staff = 'True'
    # Add all other fields...
    
    slug = AutoSlugField(populate_from='username', unique=True, null=True, default=None)


class QuoteFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Quote
    
    # text = fake.text() # 'name'
    
    text = factory.Sequence(lambda obj: fake.text())    
    contributor = factory.SubFactory(UserFactory)
    
    # Define the slug attribute directly within the factory
    slug = factory.LazyAttribute(lambda obj: obj.text[:100])
    
    # categories
    # author = factory.SubFactory(AuthorFactory)
    # likes
    # lang
    # status
    
    # date_created
    # date_updated

    # is_staff = 'True'
    

