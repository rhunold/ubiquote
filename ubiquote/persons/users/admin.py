from django.contrib import admin

from django.contrib.auth.admin import UserAdmin
from .forms import UserCreationForm, UserChangeForm

from .models import User



class UserAdmin(UserAdmin):
    add_form = UserCreationForm
    form = UserChangeForm
    model = User
    list_display = ('username', 'email', 'is_staff', 'is_active',)
    list_filter = ('email', 'is_staff', 'is_active',)
    fieldsets = (
        (None, {'fields': ('username', 'email', 'password', 'first_name', 'middle_name', 'particul', 'last_name', 'sex', 'nationality', 'biography', 'avatar',   )}),
        ('Permissions', {'fields': ('is_staff', 'is_active')}),
    )
    # add_fieldsets = (
    #     (None, {
    #         'classes': ('wide',),
    #         'fields': ('username', 'email', 'password1', 'password2', 'first_name', 'middle_name', 'particul', 'last_name', 'is_staff', 'is_active', 'sex', 'nationality', 'biography', 'avatar', 'slug')}
    #     ),
    # )
    search_fields = ('email',)
    ordering = ('email',)


admin.site.register(User, UserAdmin)
