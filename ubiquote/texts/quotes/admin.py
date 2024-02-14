from django.contrib import admin, messages

from django.urls import path, reverse
from django.shortcuts import render
from django.http import HttpResponseRedirect

from django.contrib.auth.admin import UserAdmin
from .forms import QuoteForm
from .models import Quote, QuotesCategories
from persons.authors.models import Author

from django import forms

from datetime import datetime, timedelta
import random

import re

start_date = datetime(2020, 10, 1)
end_date = datetime(2023, 10, 10)



class QuotesCategoriesInline(admin.TabularInline):
    model = QuotesCategories
    
    
class CsvImportForm(forms.Form):
    csv_upload = forms.FileField()    


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

    
    def get_urls(self):
        urls = super().get_urls()
        news_urls = [path('upload-quotes-csv/', self.upload_quotes_csv)]
        return  news_urls + urls
    
    def upload_quotes_csv(self, request):
        
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
                    
                    # print(fields[0][3:-3])
                    # print(fields[0])                    
                    # print(fields[1])
                    # print(fields[2])
                    # print(text)
                    # print(type(fields[3]))                           

                    Quote.objects.create(
                        # id = fields[0],
                        
                        # text,lang,author,work,contributor,slug,status,published,date_created,date_updated,LINE BREAKER
                        
                        text = text,
                        lang = fields[1],
                        author = Author(id=int(fields[2])),
                        # work = fields[3],
                        date_created = random_datetime,
                    )
                
            url = reverse('admin:index')
            return HttpResponseRedirect(url)
            
        
        form = CsvImportForm()
        data = {"form": form}
        return render(request, "admin/csv_quotes_upload.html", data)    
    



admin.site.register(Quote, QuoteAdmin)
