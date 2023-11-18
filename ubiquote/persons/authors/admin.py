from django.contrib import admin, messages
from .models import Author

from django.urls import path, reverse
from django.shortcuts import render
from django.http import HttpResponseRedirect


from django import forms

from .models import Author

class CsvImportForm(forms.Form):
    csv_upload = forms.FileField()

class AuthorAdmin(admin.ModelAdmin):
    
    # list_display = ('first_name', 'middle_name', 'last_name', 'nickname')
    ordering = ('last_name',)
    search_fields = ['first_name', 'middle_name', 'last_name', 'nickname']
    # autocomplete_fields = ['last_name']
    
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
                
                # print(fields[0])
                # print(fields[1])                
                # print(fields[2])
                # print(fields[3])
                
                created_author = Author.objects.update_or_create(
                    id = fields[0],
                    first_name = fields[1],
                    middle_name = fields[2],
                    last_name = fields[3],
                    nickname = fields[4],
                )
                
                url = reverse('admin:index')
                return HttpResponseRedirect(url)
            
        
        form = CsvImportForm()
        data = {"form": form}
        return render(request, "admin/csv_authors_upload.html", data)


admin.site.register(Author, AuthorAdmin)

