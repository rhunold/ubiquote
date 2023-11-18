from django.contrib import admin


from django.contrib.auth.admin import UserAdmin
from .forms import QuoteForm
from .models import Quote, QuotesCategories


class QuotesCategoriesInline(admin.TabularInline):
    model = QuotesCategories


class QuoteAdmin(admin.ModelAdmin):
    form = QuoteForm
    # model = Quote
    
    # fieldsets = (
    #     (None, {'fields': ('text', 'author', 'contributor', 'lang', )}),
    # )
    inlines = [QuotesCategoriesInline]   
    
    list_display = ('text', 'contributor', 'get_categories',)  
    ordering = ('-date_updated',)
    list_filter = ('categories',)
    



admin.site.register(Quote, QuoteAdmin)
