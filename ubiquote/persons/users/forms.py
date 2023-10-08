from django.contrib.auth.forms import UserCreationForm, UserChangeForm, AuthenticationForm
from django import forms
from .models import User


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
        
        
# class LoginForm(AuthenticationForm):
#     class Meta:
#         model = User
        
        
# class LogoutForm(AuthenticationForm):
#     class Meta:
#         model = User
        
