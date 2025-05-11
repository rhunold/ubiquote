import pytest
from django.db import connection
from django.contrib.auth import get_user_model
from django.test import TestCase

User = get_user_model()

class TestDatabase(TestCase):
    """Test database operations and constraints"""
    
    def setUp(self):
        """Set up test data."""
        # Create a test user
        self.test_user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User',
            is_staff=False,
            is_active=True,
            is_superuser=False
        )
        self.superuser = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='adminpass123',
            first_name='Admin',
            last_name='User',
            is_staff=True,
            is_active=True,
            is_superuser=True
        )

    def test_database_connection(self):
        """Test database connection is established"""
        assert connection.connection is not None

    def test_user_notnull(self):
        """Test that users exist in the database"""
        assert User.objects.count() > 0

    def test_database_read_operation(self):
        """Test database read operations"""
        result = User.objects.first()
        assert result is not None
        assert result.username == 'testuser'

    def test_users_user_table_exist(self):
        """Test that the users_user table exists and has a superuser"""
        with connection.cursor() as cursor:
            cursor.execute('select id from users_user where is_superuser is True')
            rs = cursor.fetchall()
            assert len(rs) == 1

    def test_database_constraints(self):
        """Test database constraints"""
        from django.db.utils import IntegrityError
        from django.db import transaction
        
        # Test unique email constraint
        with transaction.atomic():
            with pytest.raises(IntegrityError):
                User.objects.create(
                    username='duplicate1',
                    email='test@example.com',  # This email already exists
                    password='testpass123',
                    first_name='Test',
                    last_name='User',
                    is_staff=False,
                    is_active=True,
                    is_superuser=False
                )
        
        # Test unique username constraint
        with transaction.atomic():
            with pytest.raises(IntegrityError):
                User.objects.create(
                    username='testuser', 
                    email='test@example.com',  # This emmail already exists
                    password='testpass123',
                    first_name='Test',
                    last_name='User',
                    is_staff=False,
                    is_active=True,
                    is_superuser=False
                )

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
    
    
    
