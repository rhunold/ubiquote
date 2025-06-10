# middleware.py
from django.http import JsonResponse
from django.shortcuts import resolve_url
from django.conf import settings
from django.shortcuts import render
from django.utils.deprecation import MiddlewareMixin



class HTMXSessionExpiryMiddleware(MiddlewareMixin):
    def process_response(self, request, response):
        if request.headers.get("HX-Request"):
            if response.status_code == 302 and response.url.startswith(resolve_url(settings.LOGIN_URL)):
                # Redirect to login, but return login form in modal instead
                login_form = render(request, "registration/modal_login.html").content.decode()
                return JsonResponse(
                    {"modal": login_form},
                    status=401,
                    headers={"HX-Trigger": "showLoginModal"}
                )
        return response

     