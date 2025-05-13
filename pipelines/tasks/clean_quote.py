from prefect import task
from texts.quotes.utils import clean_text

@task
def clean_quote_text(text, lang):
    new_text = clean_text(text, lang)
    return new_text
    
