from django import forms
from dal import autocomplete

from .models import Quote

from django.utils.translation import gettext_lazy as _




class QuoteForm(forms.ModelForm):
    
    def clean_categories(self):
        categories = self.cleaned_data.get('categories')
        if categories.count() > 3:
            raise forms.ValidationError('You can associate a maximum of 3 categories.')
        return categories
    

    class Meta:
        model = Quote
        fields = ('text', 'author', 'lang', 'categories', 'status', 'contributor') # 'contributor'
        widgets = {
            'text': forms.Textarea(attrs={'class' : 'form-control', 'placeholder' : _("Put your quote here") }),
                     
            
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
                                

            
            # 'contributor': forms.Select(attrs={'class' : 'form-control'}),
            'lang': forms.Select(attrs={'class' : 'form-control'}),
            'categories': forms.SelectMultiple(attrs={'class' : 'form-control'}),
        }

