from django import forms
# from dal import autocomplete

from .models import Author

from django.utils.translation import gettext_lazy as _


class AuthorForm(forms.ModelForm):
    class Meta:
        model = Author
        fields = ('first_name', 'middle_name', 'last_name', 'nickname', 'avatar', 'biography', 'sex') # 'contributor'
        widgets = {
            'biography': forms.Textarea(attrs={'class' : 'form-control', 'placeholder' : _("Put your bio here")}),
            
            'author': forms.Select(attrs={'class' : 'form-control'}),
            # 'author': autocomplete.ModelSelect2(url='autthor-autocomplete', attrs={'class' : 'form-control'}),
            
            'lang': forms.Select(attrs={'class' : 'form-control'}),
        }

