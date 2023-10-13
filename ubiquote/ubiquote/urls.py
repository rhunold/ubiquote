"""
URL configuration for ubiquote project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include, re_path
from django.conf.urls.i18n import i18n_patterns
from django.conf import settings
from django.conf.urls.static import static

from django.utils.translation import gettext_lazy as _

urlpatterns = [
    # path('admin/', admin.site.urls),
    path(_('admin/'), admin.site.urls),    
    # path('', include('texts.urls', namespace='texts')),    
]

urlpatterns += i18n_patterns (
    re_path(r'', include('texts.urls', namespace='texts')),
    re_path(r'', include('texts.quotes.urls', namespace='quotes')),
    re_path(r'', include('persons.users.urls', namespace='users')),            
    re_path(r'', include('persons.authors.urls', namespace='authors')),
    
    # re_path(r'', include('interactions.likes.urls', namespace='likes')),      
    
    # path('', include('texts.urls', namespace='texts')),
    # path('', include('texts.quotes.urls', namespace='quotes')),
    # path('', include('persons.users.urls', namespace='users')),    

    
)

if 'rosetta' in settings.INSTALLED_APPS:
    urlpatterns += [
        re_path(r'^rosetta/', include('rosetta.urls'))
]
    
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
