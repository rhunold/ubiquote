import csv
from django.core.management.base import BaseCommand
from texts.quotes.models import Quote
from texts.models import Category
from persons.authors.models import Author
from django.utils.text import slugify
from django.contrib import admin, messages

from texts.quotes.utils import create_quote_raw_from_row


class Command(BaseCommand):
    help = 'Import quotes from CSV efficiently'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str)

    def handle(self, *args, **options):
        file_path = options['csv_file']
        quotes = []
        with open(file_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            
            

            for row in reader:
                

            # # for row in csv_rows:
            #     # Check if the row contains triple quotes
            #     if '"""' in row:
            #         # Find the index of the first occurrence of triple quotes
            #         start_index = row.index('"""') + 3
                    
            #         # Find the index of the last occurrence of triple quotes
            #         end_index = row.rindex('"""') # - 3
                    
            #         # Extract the text between triple quotes
            #         text = row[start_index:end_index]
            #     else:
            #         # Handle cases where triple quotes are not found
            #         messages.warning(request, 'Triple quotes not found in CSV row.')
            #         continue

            #     # Remove the extracted text from the CSV row
            #     row = row.replace('"""' + text + '"""', '')

            #     # Split the remaining fields
            #     fields = row.split(',')

            #     # Temporarily disable auto_now_add if random_datetime for date_created
            #     quote = Quote()
            #     quote._meta.get_field('date_created').auto_now_add = False            
                            
                
            #     fields = row.split(',')
                
                author_id = int(row['author']) if row['author'] else 75  # default to Unknown
                # try:
                #     author = Author.objects.get(id=int(fields[2]))
                # except Author.DoesNotExist:
                #     author = Author.objects.get(id=75)  # Fallback to unknown             
                
                
                quote_raw = create_quote_raw_from_row(
                    text=row['text'].strip('"'),
                    lang=row['lang'],
                    author=Author(id=author_id),
                )
                quotes.append(quote_raw)                
                
                
                
                # quote = Quote(
                #     text=row['text'].strip('"'),
                #     author=Author(id=author_id),
                #     # author=author,
                    
                    
                #     lang=row['lang'],
                #     # status='approved',  # or draft/etc
                #     # contributor_id=int(row['contributor']) if row.get('contributor') else 1
                # )

                # quote.save()  # Now quote.id is set

                # quote.slug = f"{slugify(quote.text[:100])}-{quote.id}"
                # quote.save(update_fields=["slug"])  # Avoids updating all fields again

                # quotes.append(quote)
                
                

        # BATCH_SIZE = 100
        # for i in range(0, len(quotes), BATCH_SIZE):
        #     Quote.objects.bulk_create(quotes[i:i + BATCH_SIZE], ignore_conflicts=True)
        #     self.stdout.write(f"Imported {i + BATCH_SIZE} quotes...")

        self.stdout.write(self.style.SUCCESS(f"Successfully imported {len(quotes)} quotes."))
