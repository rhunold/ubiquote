from texts.quotes.models import QuoteRaw
from django.utils.text import slugify
from django.utils.timezone import now

from django.db import models
import re


def create_quote_raw_from_row(text, lang, author): # work_id=None, date_created=None, contributor_id=1
    """
    Crée un QuoteRaw sans nettoyage avancé (celui-ci sera fait plus tard dans Prefect ou une tâche cron)
    """
    # if not date_created:
    #     date_created = now()

    raw = QuoteRaw.objects.create(
        text=text.strip(),  # un minimum de nettoyage
        lang=lang,
        author=author,
        # work_id=work_id,
        # contributor_id=contributor_id,
        # date_created=date_created,
        # processed=False
    )

    raw.slug = slugify(text[:100]) + f"-{raw.id}"
    raw.save(update_fields=["slug"])

    return raw



def apply_french_rules(text):
    
    # add a space after a comma (,)   
    text = re.sub(r',(\S)', r', \1', text)
    
    # rules for semicolon (;) comma before and after comma
    text = re.sub(r';', r' ; ', text)
    
    
    # Add space before and after  "!"
    text = re.sub(r'\s*!\s*', ' ! ', text)

    # Add space before and after  "?"
    text = re.sub(r'\s*\?\s*', ' ? ', text)
    
    # when '...' then add space after but not before
    text = re.sub(r'\.{3,}\w', r'\... ', text)
    
    
    # Add more French rules here if needed

    return text

def apply_english_rules(text):
    # Example English rule: Insert your English-specific rule here // Maybe I can use it to switch some issue with author name (plato/platon) ?
    # For example, replace all occurrences of 'color' with 'colour'  
    text = re.sub(r'\bcolor\b', 'colour', text, flags=re.IGNORECASE)

    return text

def clean_text(text, lang):
    
    # print('test')
        
        
    # print(text, lang)
    # # if not lang:
    # #     return text.strip()  # fallback if lang is unknown


    # # Common rules here if needed  for all languages
    
    
  
    
    # Remove 2 or more consecutive whitespace 
    text = re.sub(r'\s\s+', ' ', text)
    
    # Uppercase the first letter of the text if it starts with a lowercase letter
    if text[0].islower():
        text = text.capitalize()      
    
    # before a  dot, remove a space if there is one
    # re.sub(r'\s\.', '\.', text)
    
    # Rules to remove space if at the start and/or end of text.
    re.sub(r'^\s+|\s+(?=\.)|\s+$', '', text)
    
    # After a dot, put a space 
    text = re.sub(r'\.(?!(\.\.\.))(\S)', r'. \2', text)
    
    # If there is no dot at the end,
    if not text.endswith('.'):
        text += '.'
        
    # The first letter of word after a . is a uppercased
    text = re.sub(r'\.(\s*)(\w)', lambda x: f'.{x.group(1)}{x.group(2).capitalize()}', text)            
        
    # The first letter of word after a ? is a uppercased
    text = re.sub(r'\?(\s*)(\w)', lambda x: f'?{x.group(1)}{x.group(2).capitalize()}', text)
        
    # print("new process going on")
    
    # return text 

    # print("passe par utils.py")


    if lang == "fr":
        return apply_french_rules(text)
    elif lang == "en":
        return apply_english_rules(text)
    else:
        
        return text  # return unchanged for other langs



