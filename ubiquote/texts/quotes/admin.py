from django.contrib import admin, messages

from django.urls import path, reverse
from django.shortcuts import render
from django.http import HttpResponseRedirect

from django.contrib.auth.admin import UserAdmin
from .forms import QuoteForm, QuoteRawForm
from .models import Quote, QuotesCategories, QuotesLikes, UserQuoteRecommendation, QuoteRaw
from persons.authors.models import Author

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

start_date = make_aware(datetime(2020, 1, 1))
end_date = make_aware(datetime(2025, 1, 1))

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
    
    
     


class QuoteRawAdmin(admin.ModelAdmin):
    form = QuoteRawForm
    # model = Quote
    
    # fieldsets = (
    #     (None, {'fields': ('text', 'author', 'contributor', 'lang', )}),
    # )
 
    
    list_display = ('text', 'author', 'processed')  # 'contributor', 'get_categories', 'slug'
    ordering = ('-date_updated',)
    # inlines = [QuotesCategoriesInline]      
    # list_filter = ('categories', )
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
                    
                    # print(fields[0][3:-3])
                    # print(fields[0])                    
                    # print(fields[1])
                    # print(fields[2])
                    # print(text)
                    # print(type(fields[3]))  
                    
                    # GÉNÉRATION DU SLUG
                    # base_slug = slugify(text[:100])  # évite des slugs trop longs
                    # slug = base_slug
                    # counter = 1
                    # while Quote.objects.filter(slug=slug).exists():
                    #     slug = f"{base_slug}-{counter}"
                    #     counter += 1                                             
                    
                    author_id = int(fields[2]) if fields[2] else 75  # default to "Unknown"
                    date_created=random_datetime
                    
                    quote_raw = create_quote_raw_from_row(
                        text=text,
                        lang=fields[1],
                        author=Author(author_id),
                        # date_created=date_created
                    ) 
                    quote_raw.save()                   
                    
                    # quote = Quote.objects.create(
                    #     # id = fields[0],
                    #     # text,lang,author,work,contributor,slug,status,published,date_created,date_updated,LINE BREAKER
                    #     text = text,
                    #     lang = fields[1],
                    #     # author = Author(id=int(fields[2])),
                    #     author_id=author_id,
                    #     # work = fields[3],
                    #     date_created = random_datetime,
                    #     # slug = slug
                    # )
                    
                    # quote.save()
                
            url = reverse('admin:index')
            return HttpResponseRedirect(url)
            
        
        form = CsvImportForm()
        data = {"form": form}
        return render(request, "admin/csv_quotes_upload.html", data)    
    
    # def ingest_quote(self, request, queryset):
    #     # Call your Prefect flow here
    #     from ...ubiquotes.pipelines.flows import quote_ingestion_shot
    #     for quote in queryset:
    #         quote_ingestion_shot(quote.id)
    #     self.message_user(request, "Ingestion completed successfully!")
    #     return HttpResponseRedirect(reverse('admin:ubiquote_quoteraw_changelist'))    
            
        
    #     if request.method == "POST":
    #         csv_file = request.FILES.get("csv_upload")

    #         if not csv_file or not csv_file.name.endswith(".csv"):
    #             messages.warning(request, "Fichier CSV invalide.")
    #             return HttpResponseRedirect(request.path_info)

    #         try:
    #             decoded = csv_file.read().decode("utf-8")
    #             raw_rows = decoded.strip().split("||")
    #         except Exception as e:
    #             messages.error(request, f"Erreur de lecture du fichier: {e}")
    #             return HttpResponseRedirect(request.path_info)

    #         start_date = now() - timedelta(days=365 * 10)
    #         end_date = now()

    #         created, skipped, errors = 0, 0, 0
    #         quotes_to_create = []

    #         with transaction.atomic():
    #             for row in raw_rows:
    #                 row = row.strip()
    #                 if not row:
    #                     continue

    #                 try:
    #                     text_match = re.search(r'"""(.*?)"""', row, re.DOTALL)
    #                     if not text_match:
    #                         skipped += 1
    #                         continue

    #                     text = text_match.group(1).strip()
    #                     row_clean = re.sub(r'""".*?"""', '', row, flags=re.DOTALL).strip()
    #                     fields = [f.strip() for f in row_clean.split(',')]

    #                     if len(fields) < 3:
    #                         skipped += 1
    #                         continue

    #                     lang = fields[1]
    #                     author_id = fields[2]

    #                     if not author_id.isdigit():
    #                         skipped += 1
    #                         continue

    #                     try:
    #                         author = Author.objects.get(id=int(author_id))
    #                     except Author.DoesNotExist:
    #                         skipped += 1
    #                         continue

    #                     random_date = start_date + timedelta(
    #                         days=random.randint(0, (end_date - start_date).days),
    #                         hours=random.randint(0, 23),
    #                         minutes=random.randint(0, 59)
    #                     )

    #                     quotes_to_create.append(Quote(
    #                         text=text,
    #                         lang=lang,
    #                         author=author,
    #                         date_created=random_date
    #                     ))

    #                 except Exception as e:
    #                     print(f"Erreur ligne: {e}")
    #                     errors += 1

    #             if quotes_to_create:
    #                 Quote.objects.bulk_create(quotes_to_create)
    #                 created = len(quotes_to_create)

    #         messages.success(
    #             request,
    #             f"{created} quotes créés, {skipped} ignorés, {errors} en erreur."
    #         )
    #         return HttpResponseRedirect(reverse('admin:index'))

    #     # GET request
    #     form = CsvImportForm()
    #     return render(request, "admin/csv_quotes_upload.html", {"form": form})    
    
    
    # 
        
        
    #     if request.method == "POST":
    #         csv_file = request.FILES.get("csv_upload")

    #         if not csv_file or not csv_file.name.endswith(".csv"):
    #             messages.warning(request, "Fichier CSV invalide.")
    #             return HttpResponseRedirect(request.path_info)

    #         try:
    #             decoded = csv_file.read().decode("utf-8")
    #             raw_rows = decoded.strip().split("||")
    #         except Exception as e:
    #             messages.error(request, f"Erreur de lecture du fichier: {e}")
    #             return HttpResponseRedirect(request.path_info)

    #         start_date = now() - timedelta(days=365 * 10)
    #         end_date = now()
    #         created, skipped, errors = 0, 0, 0
    #         quotes_to_create = []

    #         for row in raw_rows:
    #             row = row.strip()
    #             if not row:
    #                 continue

    #             try:
    #                 # extract text between triple quotes
    #                 text_match = re.search(r'"""(.*?)"""', row, re.DOTALL)
    #                 if not text_match:
    #                     skipped += 1
    #                     continue

    #                 text = text_match.group(1).strip()
    #                 row_clean = re.sub(r'""".*?"""', '', row, flags=re.DOTALL).strip()
    #                 fields = [f.strip() for f in row_clean.split(',')]

    #                 if len(fields) < 3:
    #                     skipped += 1
    #                     continue

    #                 lang = fields[1]
    #                 author_id = fields[2]

    #                 if not author_id.isdigit():
    #                     skipped += 1
    #                     continue

    #                 try:
    #                     author = Author.objects.get(id=int(author_id))
    #                 except Author.DoesNotExist:
    #                     skipped += 1
    #                     continue

    #                 random_date = start_date + timedelta(
    #                     days=random.randint(0, (end_date - start_date).days),
    #                     hours=random.randint(0, 23),
    #                     minutes=random.randint(0, 59)
    #                 )

    #                 quotes_to_create.append(Quote(
    #                     text=text,
    #                     lang=lang,
    #                     author=author,
    #                     date_created=random_date
    #                 ))

    #             except Exception as e:
    #                 print(f"Erreur ligne: {e}")
    #                 errors += 1

    #         if quotes_to_create:
    #             Quote.objects.bulk_create(quotes_to_create)
    #             created = len(quotes_to_create)

    #         messages.success(
    #             request,
    #             f"{created} créés, {skipped} ignorés, {errors} en erreur."
    #         )
    #         return HttpResponseRedirect(reverse('admin:index'))
        
    #     # GET
    #     form = CsvImportForm()
    #     return render(request, "admin/csv_quotes_upload.html", {"form": form})        
            
            
    #     # ----------------------------------
            
    #     # if request.method == "POST":
    #     #     csv_file = request.FILES.get("csv_upload")

    #     #     if not csv_file or not csv_file.name.endswith('.csv'):
    #     #         messages.warning(request, 'Fichier CSV invalide.')
    #     #         return HttpResponseRedirect(request.path_info)

    #     #     file_data = csv_file.read().decode("utf-8")
    #     #     rows = file_data.split("||")

    #     #     created, skipped, errors = 0, 0, 0
    #     #     end_date = now()
    #     #     start_date = end_date - timedelta(days=365 * 10)

    #     #     for row in rows:
    #     #         row = row.strip()
    #     #         if not row:
    #     #             continue

    #     #         try:
    #     #             reader = csv.reader([row])
    #     #             fields = next(reader)

    #     #             # Vérifie que les champs essentiels sont présents
    #     #             if len(fields) < 3:
    #     #                 skipped += 1
    #     #                 continue

    #     #             text = fields[0].strip().replace('""', '"').strip('" ')
    #     #             lang = fields[1].strip()
    #     #             author_id = fields[2].strip()

    #     #             if not text or not lang or not author_id.isdigit():
    #     #                 skipped += 1
    #     #                 continue

    #     #             try:
    #     #                 author = Author.objects.get(id=int(author_id))
    #     #             except Author.DoesNotExist:
    #     #                 skipped += 1
    #     #                 continue

    #     #             # Génère une date aléatoire
    #     #             random_datetime = start_date + timedelta(
    #     #                 days=random.randint(0, (end_date - start_date).days),
    #     #                 hours=random.randint(0, 23),
    #     #                 minutes=random.randint(0, 59)
    #     #             )

    #     #             Quote.objects.create(
    #     #                 text=text,
    #     #                 lang=lang,
    #     #                 author=author,
    #     #                 date_created=random_datetime
    #     #             )
    #     #             created += 1

    #     #         except Exception as e:
    #     #             print(f"Ligne ignorée pour cause d’erreur : {e}")
    #     #             errors += 1

    #     #     messages.success(request, f"{created} quotes créées, {skipped} ignorées, {errors} en erreur.")
    #     #     return HttpResponseRedirect(reverse('admin:index'))

    #     # form = CsvImportForm()
    #     # return render(request, "admin/csv_quotes_upload.html", {"form": form})        
        
    #     # --------------------------
        
    #     # if request.method == "POST":
    #     #     csv_file = request.FILES.get("csv_upload")
    #     #     if not csv_file or not csv_file.name.endswith(".csv"):
    #     #         messages.warning(request, "Invalid file type.")
    #     #         return redirect(request.path_info)

    #     #     try:
    #     #         decoded_file = TextIOWrapper(csv_file.file, encoding="utf-8")
    #     #         raw_content = decoded_file.read()
    #     #     except Exception as e:
    #     #         messages.error(request, f"Could not read CSV file: {e}")
    #     #         return redirect(request.path_info)

    #     #     # Split rows on custom delimiter
    #     #     csv_rows = raw_content.strip().split("||")
    #     #     if not csv_rows or len(csv_rows) < 2:
    #     #         messages.warning(request, "No valid rows found.")
    #     #         return redirect(request.path_info)
            
    #     #     start_date = datetime(2020, 10, 1)
    #     #     end_date = datetime(2023, 10, 10)            

    #     #     # start_date = ...  # Set this to your desired start date
    #     #     # end_date = ...    # Set this to your desired end date
    #     #     now_func = lambda: start_date + timedelta(
    #     #         days=random.randint(0, (end_date - start_date).days),
    #     #         hours=random.randint(0, 23),
    #     #         minutes=random.randint(0, 59)
    #     #     )

    #     #     quotes_to_create = []
    #     #     BATCH_SIZE = 500

    #     #     try:
    #     #         with transaction.atomic():
    #     #             for row in csv_rows[1:]:  # Skip header
    #     #                 try:
    #     #                     # Extract text between triple quotes
    #     #                     text_match = re.search(r'"""(.*?)"""', row, re.DOTALL)
    #     #                     if not text_match:
    #     #                         continue
    #     #                     text = text_match.group(1).strip()
    #     #                     row_clean = re.sub(r'""".*?"""', '', row, flags=re.DOTALL).strip()
    #     #                     fields = [f.strip() for f in row_clean.split(',')]

    #     #                     if len(fields) < 3:
    #     #                         continue  # not enough data

    #     #                     quote = Quote(
    #     #                         text=text,
    #     #                         lang=fields[1],
    #     #                         author = Author(id=int(fields[2])),  # assumes ID exists
    #     #                         date_created=now_func(),
    #     #                     )
    #     #                     quotes_to_create.append(quote)

    #     #                     if len(quotes_to_create) >= BATCH_SIZE:
    #     #                         Quote.objects.bulk_create(quotes_to_create, ignore_conflicts=True)
    #     #                         quotes_to_create.clear()

    #     #                 except Exception as row_error:
    #     #                     # Skip row but continue
    #     #                     print(f"Skipping row due to error: {row_error}")
    #     #                     continue

    #     #             if quotes_to_create:
    #     #                 Quote.objects.bulk_create(quotes_to_create, ignore_conflicts=True)

    #     #     except Exception as e:
    #     #         messages.error(request, f"Upload failed: {e}")
    #     #         return redirect(request.path_info)

    #     #     messages.success(request, "Quotes uploaded successfully.")
    #     #     return redirect(reverse("admin:index"))

    #     # # # GET
    #     # # form = CsvImportForm()
    #     # # return render(request, "admin/csv_quotes_upload.html", {"form": form})   
    
    #     # form = CsvImportForm()
    #     # data = {"form": form}
    #     # return render(request, "admin/csv_quotes_upload.html", data)            
        
        

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
