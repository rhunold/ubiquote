from prefect import task
from texts.quotes.models import Quote, QuoteRaw

@task
def create_final_quote(quote_raw_id, cleaned_text):
    # from texts.quotes.models import QuoteRaw  # local import for Prefect compatibility

    raw = QuoteRaw.objects.get(id=quote_raw_id)

    final = Quote.objects.create(
        text=cleaned_text,
        lang=raw.lang,
        # slug=raw.slug,
        author=raw.author,
        # work=raw.work,
        # contributor=raw.contributor,
        # date_created=raw.date_created,
    )
    
    raw.processed = True
    raw.save()

    return final.id
