from django.conf import settings
from django.shortcuts import redirect, render
import requests
import logging
from django.core.cache import cache
from django.contrib.auth import logout
from django.contrib import messages
from django.utils.translation import get_language

from django.http import JsonResponse
from rest_framework_simplejwt.views import TokenRefreshView


# Set up logger for error handling
logger = logging.getLogger(__name__)


class RefreshTokenView(TokenRefreshView):
    """
    A view to refresh access tokens using the refresh token stored in session.
    """
    def post(self, request, *args, **kwargs):
        refresh = request.session.get('refresh_token')
        if not refresh:
            return JsonResponse({'detail': 'No refresh token found in session'}, status=401)

        request.data._mutable = True  # Only needed for QueryDict
        request.data['refresh'] = refresh
        request.data._mutable = False

        response = super().post(request, *args, **kwargs)

        # Optional: update session tokens here
        if response.status_code == 200:
            data = response.data
            request.session['access_token'] = data.get('access')
            if 'refresh' in data:
                request.session['refresh_token'] = data.get('refresh')

        return response

class TokenRefreshMixin:
    """Mixin to handle access token refresh and user logout on token expiry."""

    def refresh_access_token(self):
        try:
            response = self.request.post(f'{settings.API_URL}/token/refresh-session/')
            if response.status_code == 200:
                data = response.json()
                return data.get('access')
            else:
                return self.handle_token_expiry()
        except requests.RequestException as e:
            logger.error(f"Exception refreshing token via session: {e}")
            return self.handle_token_expiry()        
        # refresh_token = self.request.session.get('refresh_token')
        # if refresh_token:
        #     try:
        #         response = requests.post(
        #             f'{settings.API_URL}token/refresh/',
        #             json={'refresh': refresh_token},
        #             headers={'Content-Type': 'application/json'},
        #         )
        #         if response.status_code == 200:
        #             data = response.json()
        #             new_access_token = data.get('access')
        #             new_refresh_token = data.get('refresh', refresh_token)  # Update if token rotation
        #             self.request.session['access_token'] = new_access_token
        #             self.request.session['refresh_token'] = new_refresh_token
        #             return new_access_token
        #         else:
        #             # If token refresh fails, handle token expiry
        #             return self.handle_token_expiry()
        #     except requests.RequestException as e:
        #         # Log the exception
        #         logger.error(f"Exception when refreshing token: {e}")
        #         return self.handle_token_expiry()
        # return self.handle_token_expiry()

    def handle_token_expiry(self):
        """Handle token expiry by logging out the user and redirecting."""
        # Clear the session tokens
        self.request.session.pop('access_token', None)
        self.request.session.pop('refresh_token', None)

        # Log out the user and redirect to the login page
        logout(self.request)

        # Get the current page URL for redirection after login
        current_url = self.request.build_absolute_uri()

        # Redirect to the login page with 'next' parameter for redirection after login
        return redirect(f'/login/?next={current_url}')
    
    
class DataFetchingMixin(TokenRefreshMixin):
    # api_url = None  # Set in the child class
    
    
        
    def get_api_data(self, page_number, endpoint='quotes/', search_query='', disable_cache=False): 
        """Fetch quotes from the API with error handling and caching."""
        if not self.api_url:
            logger.error("API URL not set in the view")
            return {'results': [], 'count': 0, 'detail': 'Configuration error'}
        

        api_url = f'{self.api_url}{endpoint}?page={page_number}&q={search_query}'
        headers = {}

        # Add authorization header only if the user is authenticated (token exists)
        access_token = self.request.session.get("access_token")
        if access_token:
            headers['Authorization'] = f'Bearer {access_token}'

        try:
            response = requests.get(api_url, headers=headers, timeout=10)  # Add timeout
            
            # Handle token refresh if authenticated and the token is expired
            if response.status_code == 401 and access_token:
                new_access_token = self.refresh_access_token()
                if new_access_token:
                    headers['Authorization'] = f'Bearer {new_access_token}'
                    response = requests.get(api_url, headers=headers, timeout=10)

            # Log non-200 responses
            if response.status_code != 200:
                logger.error(f"API error: {response.status_code} - URL: {api_url}")
                if response.content:
                    logger.error(f"API response: {response.content.decode()}")
                return {'results': [], 'count': 0, 'detail': f'API error: {response.status_code}'}
            
            try:
                data = response.json()
                return data
            except ValueError as e:
                logger.error(f"JSON decode error: {str(e)} - Content: {response.content.decode()}")
                return {'results': [], 'count': 0, 'detail': 'Invalid JSON response'}
            
        except requests.exceptions.Timeout:
            logger.error(f"API timeout: {api_url}")
            return {'results': [], 'count': 0, 'detail': 'API request timed out'}
        except requests.exceptions.RequestException as e:
            logger.error(f"API request error: {str(e)} - URL: {api_url}")
            return {'results': [], 'count': 0, 'detail': 'API request failed'}

    def create_api_data(self, endpoint, data):
        """Create a new resource through the API."""
        api_url = f'{self.api_url}{endpoint}'
        headers = {
            'Content-Type': 'application/json'
        }
        
        # Add authorization header if user is authenticated
        access_token = self.request.session.get("access_token")
        if access_token:
            headers['Authorization'] = f'Bearer {access_token}'
        
        try:
            response = requests.post(api_url, json=data, headers=headers)
            
            # Handle token refresh if authenticated and token is expired
            if response.status_code == 401 and access_token:
                new_access_token = self.refresh_access_token()
                if new_access_token:
                    headers['Authorization'] = f'Bearer {new_access_token}'
                    response = requests.post(api_url, json=data, headers=headers)
            
            return response.json() if response.status_code in [200, 201] else None
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error creating data through API: {e}")
            return None


    def update_api_data(self, endpoint, data, method='patch'):
        """Update a resource through the API using JWT auth."""
        url = f'{self.api_url}{endpoint}'
        headers = {
            'Content-Type': 'application/json'
        }

        access_token = self.request.session.get("access_token")
        if access_token:
            headers['Authorization'] = f'Bearer {access_token}'

        method_func = {
            'patch': requests.patch,
            'put': requests.put,
        }.get(method.lower())

        if not method_func:
            raise ValueError(f"Unsupported HTTP method: {method}")

        try:
            response = method_func(url, json=data, headers=headers)

            # Retry once if token expired
            if response.status_code == 401 and access_token:
                new_token = self.refresh_access_token()
                if new_token:
                    headers['Authorization'] = f'Bearer {new_token}'
                    response = method_func(url, json=data, headers=headers)

            if response.status_code in [200, 202]:
                return response.json()

            logger.warning(f"API update failed: {response.status_code} - {response.text}")
            return None

        except requests.RequestException as e:
            logger.error(f"RequestException while updating quote: {e}")
            return None
        

    def delete_api_data(self, endpoint):
        """Delete a resource through the API."""
        api_url = f'{self.api_url}{endpoint}'
        headers = {}
        
        # Add authorization header if user is authenticated
        access_token = self.request.session.get("access_token")
        if access_token:
            headers['Authorization'] = f'Bearer {access_token}'
        
        try:
            response = requests.delete(api_url, headers=headers)
            
            # Handle token refresh if authenticated and token is expired
            if response.status_code == 401 and access_token:
                new_access_token = self.refresh_access_token()
                if new_access_token:
                    headers['Authorization'] = f'Bearer {new_access_token}'
                    response = requests.delete(api_url, headers=headers)
            
            return response.status_code == 204  # Returns True if deletion was successful
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error deleting data through API: {e}")
            return False

    def process_pagination(self, data, request):
        """Helper method to handle pagination and URL manipulation."""
        next_page_url = data.get('next')
        previous_page_url = data.get('previous')
        
        lang = request.LANGUAGE_CODE
        if next_page_url:
            next_page_url = next_page_url.replace(f'/api/', f'/{lang}/')
        if previous_page_url:
            previous_page_url = previous_page_url.replace(f'/api/', f'/{lang}/')
        return next_page_url, previous_page_url

    def render_htmx_or_full_quotes(self, request, context):
        """Render partial or full template based on the request type (HTMX or not)."""
        try:
            if request.htmx:
                return render(request, 'partials/quotes_cards.html', context)
            return render(request, self.template_name, context)
        except Exception as e:
            logger.error(f"Template rendering error: {str(e)}")
            messages.error(request, "An error occurred while rendering the page.")
            return redirect('quotes:get-quotes')

    def render_htmx_or_full_authors(self, request, context):
        """Render partial or full template based on the request type (HTMX or not)."""
        try:
            if request.htmx:
                return render(request, 'partials/authors_cards.html', context)
            return render(request, self.template_name, context)
        except Exception as e:
            logger.error(f"Template rendering error: {str(e)}")
            messages.error(request, "An error occurred while rendering the page.")
            return redirect('authors:get-authors')
    

    

# class CleaningMixin:
#     def clean_fields(self):
#         print("Cleaning process")
        
        
        # self.text = self.text.strip()
        # if not self.lang:
        #     try:
        #         self.lang = detect(self.text)
        #     except Exception:
        #         self.lang = None

        # if not self.author_name:
        #     self.needs_review = True