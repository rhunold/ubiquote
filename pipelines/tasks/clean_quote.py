from prefect import task
# from django.utils.text import slugify
# from langdetect import detect
from texts.quotes.utils import clean_text

# from ubiquote.texts.quotes.utils import clean_text


@task
def clean_quote_text(text, lang):
    
    
    # text = text.upper()
    # text = ''.join(text.split())
    
    new_text = clean_text(text, lang)
    
    # print(text)
    # print(new_text)    
    # print("------------------")    
    # print(lang)    
    
    return new_text
    

    # text = text.strip()
    # lang = None
    # try:
    #     lang = detect(text)
    # except Exception:
    #     pass
    # return text, lang
