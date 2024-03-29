from django.contrib import admin, messages
from .models import Author, AuthorTranslation

from django.urls import path, reverse
from django.shortcuts import render
from django.http import HttpResponseRedirect

# from rosetta.admin import TranslationAdmin
from .forms import AuthorForm, AuthorTranslationForm
from django import forms

from .models import Author


from datetime import datetime, timedelta
import random

from dal import autocomplete

start_date = datetime(2020, 10, 1)
end_date = datetime(2023, 10, 10)


class CsvImportForm(forms.Form):
    csv_upload = forms.FileField()

class AuthorAdmin(admin.ModelAdmin):
    form = AuthorForm    
    
    list_display = ('first_name', 'middle_name',  'particul', 'last_name', 'nickname', 'date_created', 'date_birth', 'slug' ) # 'test_date'
    ordering = ('fullname',)
    search_fields = ['first_name', 'middle_name', 'last_name', 'nickname', 'title', 'particul']
    # autocomplete_fields = ['last_name']

    # widgets = {
    #     'date_birth': forms.DateInput(format='%Y-%m-%d'),   
    # }    

    
    def get_urls(self):
        urls = super().get_urls()
        news_urls = [path('upload-authors-csv/', self.upload_authors_csv)]
        return  news_urls + urls
    
    def upload_authors_csv(self, request):
        
        if request.method == "POST":
            # print('Action is a post')
            csv_file = request.FILES["csv_upload"]
            
            if not csv_file.name.endswith('.csv'):
                messages.warning(request, 'The wrong file type was uploaded.')
                return HttpResponseRedirect(request.path_info)
            
            
            file_data = csv_file.read().decode("utf-8")
            csv_data = file_data.split("\n")
            
            # Skip the header (first line)
            csv_rows = csv_data[1:]            
            
            for x in csv_rows:
                fields = x.split(',')
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


                # Temporarily disable auto_now_add if random_datetime for date_created
                author = Author()
                author._meta.get_field('date_created').auto_now_add = False
                
                if len(fields) >= 7:
                    
                    # print(fields[0])

                    created_author = Author.objects.update_or_create(
                        id = fields[0],
                        first_name = fields[1],
                        middle_name = fields[2],
                        particul = fields[3],
                        last_name = fields[4],
                        nickname = fields[5],
                        title = fields[6],
                        date_created = random_datetime,
                    )
                
            url = reverse('admin:index')
            return HttpResponseRedirect(url)
            
        
        form = CsvImportForm()
        data = {"form": form}
        return render(request, "admin/csv_authors_upload.html", data)


class AuthorTranslationAdmin(admin.ModelAdmin):
    form = AuthorTranslationForm   
    
    # class Meta:
    #     model = AuthorTranslation
    #     fields = ('author', 'language_code', 'translated_name') # 'contributor'
    #     widgets = {
    #         # 'text': forms.Textarea(attrs={'class' : 'form-control', 'placeholder' : _("Put your quote here") }),
                     
            
    #         'author': autocomplete.ModelSelect2(
    #             url='author-autocomplete',
    #             attrs={
    #                 # 'data-width': '100%',
    #                 'data-html': True,
    #                 # Set some placeholder
    #                 # 'data-placeholder': 'Autocomplete ...',
    #                 # Only trigger autocompletion after 2 characters have been typed
    #                 'data-minimum-input-length': 2,                    
    #                 'class' : 'form-control',
    #                 },
    #             # attrs={'class' : 'form-control'},
    #             ),
                                

            
    #         # 'contributor': forms.Select(attrs={'class' : 'form-control'}),
    #         'language_code': forms.Select(attrs={'class' : 'form-control'}),
    #         'translated_name': forms.CharField(attrs={'class' : 'form-control'}),
    #     }
    

admin.site.register(Author, AuthorAdmin)

admin.site.register(AuthorTranslation, AuthorTranslationAdmin)
