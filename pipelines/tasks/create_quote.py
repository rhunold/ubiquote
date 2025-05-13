from prefect import task
from texts.quotes.models import Quote, QuoteRaw




@task
def create_final_quote(quoteraw_id, cleaned_text, dimensions, categories,author):
    # from texts.quotes.models import QuoteRaw  # local import for Prefect compatibility

    raw = QuoteRaw.objects.get(id=quoteraw_id)

    final = Quote.objects.create(
        text=cleaned_text,
        lang=raw.lang,
        dimensions=dimensions,        
        # slug=raw.slug,
        author=author,
        # work=raw.work,
        # contributor=raw.contributor,
        # date_created=raw.date_created,
    )
    
    # Do not rerun the methods to get dimensions and cat in the Quote.save custom 
    final.save(enrich=False)
    
    if categories:
        final.categories.set(categories)    
    
    raw.processed = True
    raw.save()

    return final.id

