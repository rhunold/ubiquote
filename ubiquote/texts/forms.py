from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django import forms

from .models import User, Quote

class QuoteForm(forms.ModelForm):
    
    class Meta:
        model = Quote
        fields = ('text', 'author', 'contributor', 'lang')
        widgets = {
            'text': forms.Textarea(attrs={'class' : 'form-control', 'placeholder' : "Put your quote here"}),
            'author': forms.Select(attrs={'class' : 'form-control'}),
            'contributor': forms.Select(attrs={'class' : 'form-control'}),
            'lang': forms.Select(attrs={'class' : 'form-control'})
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
