from prefect import flow
from texts.quotes.models import QuoteRaw, Quote
from persons.authors.models import Author
from tasks.clean_quote import clean_quote_text
from tasks.duplicate_quote import check_for_duplicate_quote
from tasks.llm_quote import enrich_quote_and_assign_categories
from tasks.create_quote import create_final_quote
from django.utils.text import slugify
import time

@flow(name="quote_ingestion_flow")
def quote_ingestion_flow(limit: int = 2):
    quotes_to_process = QuoteRaw.objects.filter(processed=False).order_by('-date_created')[:limit]
    futures = []

    for raw in quotes_to_process:
        cleaned_text = clean_quote_text(raw.text, raw.lang)
        

        author_id = raw.author_id  # ou raw.author.id si FK
        
        result = check_for_duplicate_quote(cleaned_text, author_id)

        status = result["status"]

        if status == "no_duplicate":
            dimensions, categories = enrich_quote_and_assign_categories(cleaned_text)
            author = Author.objects.get(id=author_id)  
            # ✅ Création de la quote finale
            f = create_final_quote.submit(raw.id, cleaned_text, dimensions, categories, author)
            futures.append(f)            
            
            # pass  # keep original author_id
        elif status == "upgrade_author":
            # ✅ Replace author in the existing quote
            quote_id = result["quote_id"]
            new_author = Author.objects.get(id=result["new_author_id"])
            quote = Quote.objects.get(id=quote_id)

            quote.author = new_author
            quote.save()

            # ✅ mark raw as processed and skip creation
            raw.processed = True
            raw.save()
            print(f"✔ Author upgraded on existing quote {quote_id}")
            continue      

        elif status == "duplicate_skip":
            # 🚫 Duplicate exists with valid author → skip
            raw.processed = True
            raw.save()
            print("❌ Duplicate found, existing quote already has a valid author.")
            continue


        
        time.sleep(0.1)
        print(status)

    for f in futures:
        f.result()        

    #     # ⛔️ Check for duplicates
    #     result = check_for_duplicate_quote(cleaned_text, author_id)

    #     status = result["status"]

    #     if status == "no_duplicate":
    #         dimensions, categories = enrich_quote_and_assign_categories(cleaned_text)
    #         f = create_final_quote.submit(raw.id, cleaned_text, dimensions, categories)
    #         futures.append(f)
            

    #     elif status == "replace":

    #         dimensions, categories = enrich_quote_and_assign_categories(cleaned_text)
    #         Quote.objects.filter(id=result["existing_id"]).delete()            
            
    #         f = create_final_quote.submit(raw.id, cleaned_text, dimensions, categories)
    #         futures.append(f)

    #     elif status == "duplicate_found":
    #         print(f"❌ Quote ignorée (doublon trouvé ID={result['existing_id']})")
    #         raw.processed = True
    #         raw.save()
            
    #     print(status)

    #     time.sleep(0.1)

    # for f in futures:
    #     f.result()



# @flow(name="quote_ingestion_shot")
# def quote_ingestion_shot(id):
#     # try:
#     #     quotes_to_process = QuoteRaw.objects.filter(id=id)
#     # except QuoteRaw.DoesNotExist:
#     #     print(f"Quote with ID {quoteraw.id} does not exist")
#     # except Exception as e:
#     #     print(f"An error occurred: {e}")        
        
#     raw = QuoteRaw.objects.filter(id=id)

        
#     cleaned_text = clean_quote_text(raw.text)
#     # # print(cleaned_text)
#     raw.text = cleaned_text
#     # raw.lang = raw.lang
#     # # raw.slug = slugify(cleaned_text[:100]) + f"-{raw.id}"
#     # raw.save()

#     create_final_quote.submit(raw.id)