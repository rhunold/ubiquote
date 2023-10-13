from django import forms
from .models import Author


class AuthorForm(forms.ModelForm):
    class Meta:
        model = Author
        fields = ('first_name', 'middle_name', 'last_name', 'nickname', 'avatar', 'biography', 'sex') # 'contributor'
        # widgets = {
        #     'biography': forms.Textarea(attrs={'class' : 'form-control', 'placeholder' : "Put your bio here"}),
        #     'author': forms.Select(attrs={'class' : 'form-control'}),
        #     'lang': forms.Select(attrs={'class' : 'form-control'}),
        # }

