from django.contrib import admin
from .models import Category #, CategoryTranslation

from modeltranslation.admin import TranslationAdmin


class CategoryAdmin(TranslationAdmin):
    list_display = ('title', 'text', 'slug' )
    
# class CategoryTranslationAdmin(admin.ModelAdmin):
#     list_display = ('title',)
#     # list_filter = ('lang',)
#     search_fields = ('title', 'text')
    


admin.site.register(Category, CategoryAdmin)
# admin.site.register(CategoryTranslation, CategoryTranslationAdmin)
