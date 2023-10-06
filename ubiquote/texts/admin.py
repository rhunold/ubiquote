from django.contrib import admin

from django.contrib.auth.admin import UserAdmin
from .forms import UserCreationForm, UserChangeForm, QuoteForm

from .models import User, Author, Quote, Category, QuoteCategory


class QuoteCategoryInline(admin.TabularInline):
    model = QuoteCategory



class UserAdmin(UserAdmin):
    add_form = UserCreationForm
    form = UserChangeForm
    model = User
    list_display = ('username', 'email', 'is_staff', 'is_active',)
    list_filter = ('email', 'is_staff', 'is_active',)
    fieldsets = (
        (None, {'fields': ('username', 'email', 'password', 'first_name', 'last_name')}),
        ('Permissions', {'fields': ('is_staff', 'is_active')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'first_name', 'last_name', 'is_staff', 'is_active')}
        ),
    )
    search_fields = ('email',)
    ordering = ('email',)



class AuthorAdmin(admin.ModelAdmin):
    pass

class QuoteAdmin(admin.ModelAdmin):
    # form = QuoteForm
    # model = Quote
    
    # fieldsets = (
    #     (None, {'fields': ('text', 'author', 'contributor', 'lang', )}),
    # )
    inlines = [QuoteCategoryInline]   
    
    list_display = ('text', 'contributor', 'get_categories',)  
    ordering = ('-date_updated',)
    list_filter = ('categories',)


class CategoryAdmin(admin.ModelAdmin):
    pass



admin.site.register(User, UserAdmin)
admin.site.register(Author, AuthorAdmin)
admin.site.register(Quote, QuoteAdmin)
admin.site.register(Category, CategoryAdmin)

