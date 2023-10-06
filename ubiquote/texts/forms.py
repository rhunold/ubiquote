from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django import forms

from .models import User, Quote

class QuoteForm(forms.ModelForm):
    
    def clean_categories(self):
        categories = self.cleaned_data.get('categories')
        if categories.count() > 3:
            raise forms.ValidationError('You can associate a maximum of 3 categories.')
        return categories    
    
    class Meta:
        model = Quote
        fields = ('text', 'author', 'contributor', 'lang', 'categories')
        widgets = {
            'text': forms.Textarea(attrs={'class' : 'form-control', 'placeholder' : "Put your quote here"}),
            'author': forms.Select(attrs={'class' : 'form-control'}),
            'contributor': forms.Select(attrs={'class' : 'form-control'}),
            'lang': forms.Select(attrs={'class' : 'form-control'}),
            'categories': forms.SelectMultiple(attrs={'class' : 'form-control'}),
        }


# Admin Forms
class UserCreationForm(UserCreationForm):
# If you want to give superuser privileges to the staff users, override the save method 
    def save(self, commit=True):
        user = self.instance
        if user.is_staff:   
            user.is_superuser = True
        return super().save(commit=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name') # add any other field you want


class UserChangeForm(UserChangeForm):
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name') # add any other field you want
