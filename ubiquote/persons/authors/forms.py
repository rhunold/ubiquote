from django import forms
# from dal import autocomplete

from .models import Author
from texts.quotes.models import Quote

from dal import autocomplete
from django.utils.translation import gettext_lazy as _


class AuthorForm(forms.ModelForm):
    class Meta:
        model = Author
        fields = ('first_name', 'middle_name', 'last_name', 'nickname', 'avatar', 'biography', 'sex') # 'contributor'
     
        widgets = {
            'biography': forms.Textarea(attrs={'class' : 'form-control', 'placeholder' : _("Put your bio here")}),
                    
            
            'lang': forms.Select(attrs={'class' : 'form-control'}),
        }





class AuthorAutoCompleteForm(forms.ModelForm):
    class Meta:
        model = Author
        fields = ('first_name', 'middle_name', 'last_name', 'nickname', ) # 'contributor'
        queryset = Author.objects.all()
        # initial= Author.objects.order_by("last_name").first(),
        
        # author = Author.objects.all()        
        
        widgets = {
            # 'nickname': forms.Select(attrs={'class' : 'form-control'}),            
            'author': autocomplete.ModelSelect2(
                url='author-autocomplete',
                attrs={
                    # 'data-width': '100%',
                    'data-html': True,
                    # Set some placeholder
                    # 'data-placeholder': 'Autocomplete ...',
                    # Only trigger autocompletion after 2 characters have been typed
                    'data-minimum-input-length': 2,                    
                    'class' : 'form-control',
                    },
                # attrs={'class' : 'form-control'},
                ),
        }




