from django import forms
# from dal import autocomplete

from .models import Author, AuthorTranslation
from texts.quotes.models import Quote

from dal import autocomplete
from django.utils.translation import gettext_lazy as _

# class CustomDateWidget(forms.DateInput):
#     input_type = 'text'

#     def __init__(self, attrs=None, format='%Y/%m/%d'):
#         super().__init__(attrs={'autocomplete': 'off', 'placeholder': format}, format=format)


class AuthorForm(forms.ModelForm):
    
    # date_birth = forms.DateField(widget=CustomDateWidget)    
            
    class Meta:
        model = Author
        # fields = ('first_name', 'middle_name', 'last_name', 'nickname', 'avatar', 'biography', 'sex', 'date_birth') # 'contributor' 
        fields = '__all__'
        exclude = ('date_birth_datefield','date_death_datefield')        
        
   
     
        # date_birth = forms.DateInput(
        #      input_formats=['%Y-%m-%d'], attrs={'class': 'form-control'})     
        
        widgets = {
            'biography': forms.Textarea(attrs={'class' : 'form-control', 'placeholder' : _("Put your bio here")}),
                    
            # 'date_birth': forms.DateInput(format='%Y-%m-%d'),  
                      
            # 'date_birth': forms.DateInput(
            #     format=('%Y-%m-%d'), localize=True, attrs={'class': 'form-control'}),
         
            'lang': forms.Select(attrs={'class' : 'form-control'}),
        }
        

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Add the slug as a read-only field manually (only if instance exists)
        if self.instance and self.instance.pk:
            self.fields['slug'] = forms.CharField(
                initial=self.instance.slug,
                required=False,
                disabled=True,
                label='Slug',
                widget=forms.TextInput(attrs={'class': 'form-control'})
            )           


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




class AuthorTranslationForm(forms.ModelForm):
    list_display_links = ('first_name', 'last_name', 'nickname')     
    
    class Meta:
        model = AuthorTranslation
        fields = ('author', 'language_code', 'translated_name')
        widgets = {
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
                        
            'language_code': forms.Select(attrs={'class': 'form-control'}),
            'translated_name': forms.TextInput(attrs={'class': 'form-control'}),
        }
        
            