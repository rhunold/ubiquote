from prefect import flow
from texts.quotes.models import QuoteRaw, Quote
from persons.authors.models import Author
from tasks.clean_quote import clean_quote_text
from tasks.duplicate_quote import check_for_duplicate_quote
from tasks.llm_quote import enrich_quote_and_assign_categories
from tasks.create_quote import create_final_quote
from django.utils.text import slugify
import time


from django.core.exceptions import ValidationError

@flow(name="quote_ingestion_flow")
def quote_ingestion_flow(limit: int = 100):
    quotes_to_process = QuoteRaw.objects.filter(processed=False).order_by('-date_created')[:limit]
    futures = []

    for raw in quotes_to_process:
        cleaned_text = clean_quote_text(raw.text, raw.lang)
        
        author_id = raw.author_id  # ou raw.author.id si FK
        
        duplicate_result = check_for_duplicate_quote(cleaned_text, author_id)
        
        status = duplicate_result["status"]
        if status == "not_duplicate":
            dimensions, categories = enrich_quote_and_assign_categories(cleaned_text)
            author = Author.objects.get(id=author_id)  
            # ✅ Création de la quote finale
            f = create_final_quote.submit(raw.id, cleaned_text, dimensions, categories, author)
            futures.append(f) 
            # continue   
            # raw.processed = True   
            # raw.save(update_fields=["processed"])                                         
            
            # pass  # keep original author_id
        elif status == "upgraded_quote_author":
            # ✅ Replace author in the existing quote only if author is not Unknown
            quote_id = duplicate_result["quote_id"]
            quote = Quote.objects.get(id=quote_id)
        
            try:
                new_author = Author.objects.get(id=result["new_author_id"])
                quote.author = new_author
                quote.save() 
                # quote.save(update_fields=["author"])
                print(f"✔ Author upgraded on existing quote {quote_id}")
                # ✅ mark raw as processed and skip creation
                # raw.processed = True
                # raw.save(update_fields=["processed"])
                
                
                            
                               
            except:
                # raise ValidationError("Duplicate Quote is from Unknown")
                print(f"✔ Already a quote with an author")
                # ✅ mark raw as processed and skip creation
                # raw.processed = True 
                # raw.save(update_fields=["processed"])                
                # pass
            
            print(quote)

            # continue      

        elif status == "duplicate_quote":
            # 🚫 Duplicate exists with valid author → skip
            # raw.processed = True
            # raw.save(update_fields=["processed"])
            print("❌ Duplicate found, existing quote already has a valid author.")
            # continue
            
        raw.processed = True  
        raw.save(update_fields=["processed"])  
        # Il faudrait changer le champs date_update à chaque .save...                  

        
        time.sleep(0.1)
        print(status)

    for f in futures:
        f.result()        
