from django.contrib import admin, messages

from django.urls import path, reverse
from django.shortcuts import render
from django.http import HttpResponseRedirect

from django.contrib.auth.admin import UserAdmin
from .forms import QuoteForm, QuoteRawForm
from .models import Quote, QuotesCategories, QuotesLikes, UserQuoteRecommendation, QuoteRaw
from persons.authors.models import Author

from .utils import QuoteDuplicateException

from django import forms

from datetime import datetime, timedelta
import random

import re
import csv
from io import TextIOWrapper
from datetime import timedelta
from django.db import transaction
from django.utils.timezone import now
from django.shortcuts import redirect
from django.utils.text import slugify

from texts.quotes.utils import create_quote_raw_from_row

# start_date = datetime(2020, 10, 1)
# end_date = datetime(2023, 10, 10)

from django.utils.timezone import make_aware
from django.forms.models import BaseInlineFormSet

start_date = make_aware(datetime(2020, 1, 1))
end_date = make_aware(datetime(2025, 1, 1))


class QuotesCategoriesInlineFormSet(BaseInlineFormSet):
    def clean(self):
        super().clean()
        for form in self.forms:
            if not form.cleaned_data.get('category') and not form.cleaned_data.get('DELETE'):
                raise forms.ValidationError("Empty category selected. Either delete the row or choose a category.")
    

class QuotesCategoriesInline(admin.TabularInline):
    model = QuotesCategories
    formset = QuotesCategoriesInlineFormSet    
    extra = 0
    
    
    
class CsvImportForm(forms.Form):
    csv_upload = forms.FileField()   
    
    

class QuoteAdmin(admin.ModelAdmin):
    form = QuoteForm
    # model = Quote
    
    # fieldsets = (
    #     (None, {'fields': ('text', 'author', 'contributor', 'lang', )}),
    # )
 
    
    list_display = ('text', 'author', )  # 'contributor', 'get_categories', 'slug'
    ordering = ('-date_updated',)
    inlines = [QuotesCategoriesInline]      
    list_filter = ('categories', )
    search_fields = ['text', 'author__fullname__icontains',]
    
    # def has_add_permission(self, request):
    #     return False  # Read-only in admin if using QuoteRaw    

    
    # def get_urls(self):
    #     urls = super().get_urls()
    #     news_urls = [path('upload-quotes-csv/', self.upload_quotes_csv)]
    #     return  news_urls + urls
    
    def save_model(self, request, obj, form, change):
        try:
            obj.save()
        except QuoteDuplicateException as e:
            from django.contrib import messages
            self.message_user(request, f"Duplicate Quote: {str(e)}", level=messages.ERROR)    
    
    
     


class QuoteRawAdmin(admin.ModelAdmin):
    form = QuoteRawForm
    # model = Quote
    
    # fieldsets = (
    #     (None, {'fields': ('text', 'author', 'contributor', 'lang', )}),
    # )
 
    
    list_display = ('text', 'author', 'processed')  # 'contributor', 'get_categories', 'slug'
    ordering = ('-date_updated',)
    # inlines = [QuotesCategoriesInline]      
    list_filter = ('processed', )
    search_fields = ['text', 'author__fullname__icontains',]
    
    actions = ['ingest_quote']    
    
    # def has_add_permission(self, request):
    #     return False  # Read-only in admin if using QuoteRaw    

    
    def get_urls(self):
        urls = super().get_urls()
        news_urls = [path('upload-quotes-csv/', self.upload_quotes_csv)]
        return  news_urls + urls
    

    def upload_quotes_csv(self, request):
        

    # ----------------------------------    
        if request.method == "POST":
            # print('Action is a post')
            csv_file = request.FILES["csv_upload"]
            
            if not csv_file.name.endswith('.csv'):
                messages.warning(request, 'The wrong file type was uploaded.')
                return HttpResponseRedirect(request.path_info)
            
            
            file_data = csv_file.read().decode("utf-8")
            csv_data = file_data.split("||")
            
            # Skip the header (first line)
            csv_rows = csv_data[1:]            
            
            for row in csv_rows:
                # fields = row.split(',')
                # random_date = start_date + (end_date - start_date) * random.random()
                
                # Calculate a random number of days between start_date and end_date
                random_days = random.randint(0, (end_date - start_date).days)
                
                # Calculate random hours and minutes
                random_hours = random.randint(0, 23)
                random_minutes = random.randint(0, 59)
                
                # Combine everything to create a random date and time
                random_datetime = start_date + timedelta(
                    days=random_days,
                    hours=random_hours,
                    minutes=random_minutes
                )                


            # for row in csv_rows:
                # Check if the row contains triple quotes
                if '"""' in row:
                    # Find the index of the first occurrence of triple quotes
                    start_index = row.index('"""') + 3
                    
                    # Find the index of the last occurrence of triple quotes
                    end_index = row.rindex('"""') # - 3
                    
                    # Extract the text between triple quotes
                    text = row[start_index:end_index]
                else:
                    # Handle cases where triple quotes are not found
                    messages.warning(request, 'Triple quotes not found in CSV row.')
                    continue

                # Remove the extracted text from the CSV row
                row = row.replace('"""' + text + '"""', '')

                # Split the remaining fields
                fields = row.split(',')

                # Temporarily disable auto_now_add if random_datetime for date_created
                quote = Quote()
                quote._meta.get_field('date_created').auto_now_add = False
                
                if len(fields) >= 4:
                                                          
                    
                    author_id = int(fields[2]) if fields[2] else 75  # default to "Unknown"
                    date_created=random_datetime
                    
                    quote_raw = create_quote_raw_from_row(
                        text=text,
                        lang=fields[1],
                        author=Author(author_id),
                        # date_created=date_created
                    ) 
                    quote_raw.save()                   
                    
                
            url = reverse('admin:index')
            return HttpResponseRedirect(url)
            
        
        form = CsvImportForm()
        data = {"form": form}
        return render(request, "admin/csv_quotes_upload.html", data)    
    

class QuotesLikesAdmin(admin.ModelAdmin):
    model = QuotesLikes
    list_display = ('user', 'quote', 'timestamp',)  
    ordering = ('-timestamp',)
    list_filter = ('user',)    
    
    
class QuotesRecommandationAdmin(admin.ModelAdmin):
    model = UserQuoteRecommendation
    list_display = ('user', 'quote', 'created_at',)  
    ordering = ('created_at',)
    list_filter = ('user',)        

admin.site.register(Quote, QuoteAdmin)
admin.site.register(QuoteRaw, QuoteRawAdmin)
admin.site.register(QuotesLikes, QuotesLikesAdmin)

admin.site.register(UserQuoteRecommendation, QuotesRecommandationAdmin)
