from django.conf import settings
from django.shortcuts import redirect, render
import requests
import logging
from django.core.cache import cache
from django.contrib.auth import logout


# Set up logger for error handling
logger = logging.getLogger(__name__)

class TokenRefreshMixin:
    """Mixin to handle access token refresh and user logout on token expiry."""

    def refresh_access_token(self):
        refresh_token = self.request.session.get('refresh_token')
        if refresh_token:
            try:
                response = requests.post(
                    f'{settings.API_URL}token/refresh/',
                    json={'refresh': refresh_token},
                    headers={'Content-Type': 'application/json'},
                )
                if response.status_code == 200:
                    data = response.json()
                    new_access_token = data.get('access')
                    new_refresh_token = data.get('refresh', refresh_token)  # Update if token rotation
                    self.request.session['access_token'] = new_access_token
                    self.request.session['refresh_token'] = new_refresh_token
                    return new_access_token
                else:
                    # If token refresh fails, handle token expiry
                    return self.handle_token_expiry()
            except requests.RequestException as e:
                # Log the exception
                logger.error(f"Exception when refreshing token: {e}")
                return self.handle_token_expiry()
        return self.handle_token_expiry()

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
    api_url = None  # Set in the child class
        
    def get_api_data(self, page_number, endpoint='quotes/', search_query='', disable_cache=False): 
        """Fetch quotes from the API with error handling and caching."""
        cache_key = f'{self.api_url}_{endpoint}_page_{page_number}_query_{search_query}'

        # # Skip cache if randomization is required
        # if not disable_cache:
        #     data = cache.get(cache_key)
        #     if data:
        #         return data

        api_url = f'{self.api_url}{endpoint}?page={page_number}&q={search_query}'

        headers = {}

        # Add authorization header only if the user is authenticated (token exists)
        access_token = self.request.session.get("access_token")
        if access_token:
            headers['Authorization'] = f'Bearer {access_token}'

        try:
            response = requests.get(api_url, headers=headers)
            
            # Handle token refresh if authenticated and the token is expired
            if response.status_code == 401 and access_token:
                new_access_token = self.refresh_access_token()
                if new_access_token:
                    headers['Authorization'] = f'Bearer {new_access_token}'
                    response = requests.get(api_url, headers=headers)
                
            data = response.json()
            
            # # Only cache if caching is enabled
            # if not disable_cache:
            #     cache.set(cache_key, data)
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching data from API: {e}")
            data = {'results': [], 'count': 0}

        return data

    

    # def get_api_data(self, page_number, endpoint='quotes/', search_query=''): # endpoint='quotes/')
    #     """Fetch quotes from the API with error handling and caching."""
    #     cache_key = f'{self.api_url}_{endpoint}_page_{page_number}_query_{search_query}'
    #     data = cache.get(cache_key)

    #     if not data:
    #         api_url = f'{self.api_url}{endpoint}?page={page_number}&q={search_query}'
    #         headers = {
    #             'Authorization': f'Bearer {self.request.session.get("access_token")}',
    #         }
    #         try:
    #             response = requests.get(api_url, headers=headers)
    #             if response.status_code == 401:
    #                 new_access_token = self.refresh_access_token()
    #                 if new_access_token:
    #                     headers['Authorization'] = f'Bearer {new_access_token}'
    #                     response = requests.get(api_url, headers=headers)
    #             data = response.json()
    #             cache.set(cache_key, data)
    #         except requests.exceptions.RequestException as e:
    #             logger.error(f"Error fetching data from API: {e}")
    #             # data = {'results': [], 'count': 0, 'next': None}

    #     return data
    

    def process_pagination(self, data, request):
        """Helper method to handle pagination and URL manipulation."""
        next_page_url = data.get('next')
        previous_page_url = data.get('previous')
        # search_query = request.GET.get('q', '')   
                
        lang = request.LANGUAGE_CODE
        if next_page_url:
            next_page_url = next_page_url.replace(f'/api/', f'/{lang}/')
        if previous_page_url:
            previous_page_url = previous_page_url.replace(f'/api/', f'/{lang}/')
        return next_page_url, previous_page_url #, search_query



    def render_htmx_or_full_quotes(self, request, context):
        """Render partial or full template based on the request type (HTMX or not)."""
        if request.htmx:
        
        # # A way to deal with multiple fragments https://www.reddit.com/r/gatewayittutorials/comments/zmw3yn/django_htmx_fragment_with_header/
        # usr_username = request.POST.get("username").lower()
        # if request.headers.get("Hx-Trigger") == "first_name":
        #     field = "first_name"
        # elif request.headers.get("Hx-Trigger") == "email_addr":
        #     field = "email_addr"
        # context = { "field": field }            
            
            
            response = render(request, 'partials/quotes_cards.html', context)
            # response['HX-Reswap'] = 'innerHTML'            
            return response
            
        return render(request, self.template_name, context)
    

    

    # if request.htmx:
    #     context = {'quotes': quotes, 'search_query': search_query, 'count': count}
    #     return render(request, 'quotes/partials/quotes_list.html', context)
    # else:
    #     # Default return for non-HTMX requests
    #     return render(request, 'search_quotes.html', {'search_query': search_query, 'count': count})    
    
    def render_htmx_or_full_authors(self, request, context):
        """Render partial or full template based on the request type (HTMX or not)."""
        if request.htmx:
            return render(request, 'partials/authors_cards.html', context)
        return render(request, self.template_name, context)    