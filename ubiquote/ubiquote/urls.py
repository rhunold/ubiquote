
from django.contrib import admin
from django.urls import path, include, re_path
from django.conf.urls.i18n import i18n_patterns
from django.conf import settings
from django.conf.urls.static import static

from dal import autocomplete
import djhacker
from django import forms


from persons.authors.models import AuthorAutocomplete

from texts.quotes.models import Quote
from persons.authors.models import Author

from django.utils.translation import gettext_lazy as _

app_name = 'ubiquote'

urlpatterns = [
    # path('admin/', admin.site.urls),
    path(_('admin/'), admin.site.urls),    

    path(
        r'author-autocomplete/',
        AuthorAutocomplete.as_view(),
        name='author-autocomplete',
    ),
    

    
]

urlpatterns += i18n_patterns (
    re_path(r'', include('texts.urls', namespace='texts')),
    re_path(r'', include('texts.quotes.urls', namespace='quotes')),
    re_path(r'', include('persons.users.urls', namespace='users')),            
    re_path(r'', include('persons.authors.urls', namespace='authors')),

    
)

if 'rosetta' in settings.INSTALLED_APPS:
    urlpatterns += [
        re_path(r'^rosetta/', include('rosetta.urls'))
]
    
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    
    

djhacker.formfield(
    Quote.author,
    forms.ModelChoiceField,
    widget=autocomplete.ModelSelect2(url='ubiquote:author-autocomplete')
    )
