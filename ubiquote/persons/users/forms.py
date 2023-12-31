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
        
        
class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = '__all__'
        # fields = ('first_name', 'middle_name', 'last_name', 'nickname', 'avatar', 'biography', 'sex') # 'contributor'
        # widgets = {
        #     'biography': forms.Textarea(attrs={'class' : 'form-control', 'placeholder' : "Put your bio here"}),
        #     'author': forms.Select(attrs={'class' : 'form-control'}),
        #     'lang': forms.Select(attrs={'class' : 'form-control'}),
        # }
        
        
        
# class LoginForm(AuthenticationForm):
#     class Meta:
#         model = User
        
        
# class LogoutForm(AuthenticationForm):
#     class Meta:
#         model = User
        
