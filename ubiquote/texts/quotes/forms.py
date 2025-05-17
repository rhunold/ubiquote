from django import forms
from dal import autocomplete
import json

from .models import Quote, Author, QuoteRaw
from texts.models import Category
from .utils import clean_text

from .utils import generate_response
from .utils import QuoteDuplicateException

from django.utils.translation import gettext_lazy as _



class QuoteForm(forms.ModelForm):
    author = forms.ModelChoiceField(
        queryset=Author.objects.all(),
        required=False,
        widget=autocomplete.ModelSelect2(
            url='author-autocomplete',
            attrs={
                'data-html': True,
                'data-minimum-input-length': 2,
                'class': 'form-control',
            },
        )
    )
    

    def clean_categories(self):
        categories = self.cleaned_data.get('categories')
        if categories and categories.count() > 3:
            raise forms.ValidationError('You can associate a maximum of 3 categories.')
        return categories
    
    
    def clean_author(self):
        author = self.cleaned_data.get('author')
        if not author:
            try:
                return Author.objects.get(id=75)  # Your "Unknown" author
            except Author.DoesNotExist:
                raise forms.ValidationError("Default author Unknonw not found (ID 75).")
        return author
    


    def clean_text(self):
        text = self.cleaned_data['text']
        return clean_text(text, self.data.get('lang', None))  # pass lang to your clean_text function


    class Meta:
        model = Quote
        fields = ('text', 'author', 'lang', 'categories', 'status', 'contributor', 'dimensions')
        widgets = {
            'text': forms.Textarea(attrs={'class': 'form-control', 'placeholder': _("Put your quote here")}),
            'lang': forms.Select(attrs={'class': 'form-control'}),
            'categories': forms.SelectMultiple(attrs={'class': 'form-control'}),
            'status': forms.HiddenInput(),
            'contributor': forms.HiddenInput(),
        }
        
        

class QuoteRawForm(forms.ModelForm):
    author = forms.ModelChoiceField(
        queryset=Author.objects.all(),
        required=False,
        widget=autocomplete.ModelSelect2(
            url='author-autocomplete',
            attrs={
                'data-html': True,
                'data-minimum-input-length': 2,
                'class': 'form-control',
            },
        )
    )


    class Meta:
        model = QuoteRaw
        fields = ('text', 'author', 'lang', 'contributor')
        widgets = {
            'text': forms.Textarea(attrs={'class': 'form-control', 'placeholder': _("Put your quote here")}),
            'lang': forms.Select(attrs={'class': 'form-control'}),
            'contributor': forms.HiddenInput(),
        }        



