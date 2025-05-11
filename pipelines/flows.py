from prefect import flow
from texts.quotes.models import QuoteRaw
from tasks.clean_quote import clean_quote_text
from tasks.create_quote import create_final_quote
from django.utils.text import slugify
import time

@flow(name="quote_ingestion_flow")
def quote_ingestion_flow(limit: int = 2):
    
    
    quotes_to_process = QuoteRaw.objects.filter(processed=False).order_by('-date_created')[:limit]
    futures = []
    
    for raw in quotes_to_process:

        cleaned_text = clean_quote_text(raw.text, raw.lang)
        # raw.text = cleaned_text
        print(cleaned_text)

        f = create_final_quote.submit(raw.id, cleaned_text)
        time.sleep(0.1) 
        futures.append(f)
    
        # Attend que toutes les tâches soient finies
    for f in futures:
        f.result()



@flow(name="quote_ingestion_shot")
def quote_ingestion_shot(id):
    # try:
    #     quotes_to_process = QuoteRaw.objects.filter(id=id)
    # except QuoteRaw.DoesNotExist:
    #     print(f"Quote with ID {quoteraw.id} does not exist")
    # except Exception as e:
    #     print(f"An error occurred: {e}")        
        
    raw = QuoteRaw.objects.filter(id=id)

        
    cleaned_text = clean_quote_text(raw.text)
    # # print(cleaned_text)
    raw.text = cleaned_text
    # raw.lang = raw.lang
    # # raw.slug = slugify(cleaned_text[:100]) + f"-{raw.id}"
    # raw.save()

    create_final_quote.submit(raw.id)