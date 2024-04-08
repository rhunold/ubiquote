import pytest

from persons.users.models import User
from persons.authors.models import Author
from texts.quotes.models import Quote, QuotesLikes

from django.db import connection

# Test database 
def test_user_notnull(db):
    assert User.objects.count() != 0



def test_database_connection():
    from django.db import connection
    assert connection.connection is not None


def test_database_read_operation(db):
    # Perform a read operation
    result = User.objects.first()
    # Assert the result
    assert result is not None


def test_users_user_table_exist(db):
    with connection.cursor() as cursor:
        cursor.execute('select id from users_user where is_superuser is True')
        rs = cursor.fetchall()
        assert len(rs) == 1
        
        
def test_database_write_operation(db):
    # Perform a write operation
    obj = User.objects.create(username='Test')
    # Retrieve the object to verify
    result = User.objects.filter(username='Test').first()
    # Assert the result
    assert result is not None
        
        
def test_database_constraints(db):
    from django.db.utils import IntegrityError
    # Attempt to create an object violating a constraint
    with pytest.raises(IntegrityError):
        User.objects.create(email='test@gmail.com')  # Assuming 'email' field has a unique constraint

def test_database_transactions(db):
    from django.db import transaction
    # Start a transaction
    count_before = User.objects.count()      
    with transaction.atomic():
        # Perform database operations
        User.objects.create(email='Test1@gmail.com', username="Test1")
        User.objects.create(email='Test2@gmail.com', username="Test2")
    # Verify changes are rolled back    
    assert User.objects.count() != count_before
    




# @pytest.mark.django_db
# def test_index_usage():
#     # Execute a query that filters records based on the email column
#     query = "SELECT * FROM users_user WHERE email = 'test@gmail.com'"
    
#     # Get a cursor object to execute SQL queries
#     cursor = connection.cursor()
    
#     # Execute the query and fetch the query plan
#     cursor.execute(f"EXPLAIN {query}")
#     query_plan = cursor.fetchall()
    
#     # Check if the query plan indicates that the index is being used
#     index_used = any('users_user_email_243f6e77_like' in plan[0] for plan in query_plan)
    
#     # Assert that the index is being used
#     assert index_used, "Index on email column is not being used"


def test_database_performance():
    from time import time
    start_time = time()
    # Execute the query or operation
    User.objects.all()
    end_time = time()
    # Assert that the query executes within a reasonable time frame
    assert end_time - start_time < 1  # Example: Less than 1 second
    
    
def test_database_migrations(db, capsys):
    from django.core.management import call_command
    # Run database migrations
    call_command('migrate')
    
    # Capture the standard output to check for errors
    captured = capsys.readouterr()

    # Check if any errors occurred during migrations
    assert 'Error' not in captured.err
    
    
    
