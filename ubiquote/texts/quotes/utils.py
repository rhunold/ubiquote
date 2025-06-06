
from django.utils.text import slugify
from django.utils.timezone import now

from django.contrib.postgres.search import TrigramSimilarity
from rapidfuzz.fuzz import token_set_ratio

from django.db import models
import re

import os
import pandas as pd
import time
import ollama
import json
from typing import List

from pydantic import BaseModel, Field, ValidationError, field_validator



def create_quote_raw_from_row(text, lang, author): # work_id=None, date_created=None, contributor_id=1
    from texts.quotes.models import QuoteRaw
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

#--------------- apply clean on text ------------------


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
    # text = re.sub(r'\.(?!(\.\.\.))(\S)', r'. \2', text)
    
    # Apply space after a dot, except when it's part of an ellipsis or multiple dots
    text = re.sub(r'\.(?!\.|\s)(?!\S*\.{3})', r'. ', text)
    
    # If there is no punctiona at the end,
    if not text.endswith(('.', '!', '?')):
        text += '.'
        
    # The first letter of word after a . is a uppercased
    text = re.sub(r'\.(\s*)(\w)', lambda x: f'.{x.group(1)}{x.group(2).capitalize()}', text)            
        
    # The first letter of word after a ? is a uppercased
    text = re.sub(r'\?(\s*)(\w)', lambda x: f'?{x.group(1)}{x.group(2).capitalize()}', text)
        


    if lang == "fr":
        return apply_french_rules(text)
    elif lang == "en":
        return apply_english_rules(text)
    else:
        
        return text  # return unchanged for other langs

#--------------- detection of duplicate ------------------

class QuoteDuplicateChecker:
    def __init__(self, text, author_id, similarity_threshold=0.7, fuzz_threshold=80):
        self.text = text.strip()
        self.author_id = author_id
        self.similarity_threshold = similarity_threshold
        self.fuzz_threshold = fuzz_threshold

    def is_duplicate(self):
        from texts.quotes.models import Quote
        # Étape 1 : pré-filtrage avec trigram
        candidates = Quote.objects.annotate(
            similarity=TrigramSimilarity('text', self.text)
        ).filter(similarity__gt=self.similarity_threshold)
        # print(candidates)

        # Étape 2 : raffinement avec fuzzy matching
        for quote in candidates:
            score = token_set_ratio(quote.text, self.text)
            # print(score) # Très étrange mais ce print affiche mon module en front djdt... ???!!
            if score >= self.fuzz_threshold:
                if quote.author_id != self.author_id or self.author_id != 75:
                    return True, quote  # Doublon trouvé
        return False, None

def check_for_duplicate_quote(text: str, author_id: int) -> dict:
    from texts.quotes.models import Quote
    """
    Checks whether a quote with the same text already exists.

    Rules:
    - If no existing quote with the same text: return "not_duplicate"
    - If exists and existing author is UNKNOWN (75) and new one is different: return "upgrade_author"
    - If exists and author is already valid (≠ 75): return "duplicate_quote"

    Returns:
        dict: with keys: 'status', and sometimes 'quote_id', 'new_author_id'
    """

    try:
        existing_quote = Quote.objects.get(text__iexact=text)
    except Quote.DoesNotExist:
        return {"status": "not_duplicate"}

    # Case 1: Existing quote has UNKNOWN author and we have a better one
    if existing_quote.author_id == 75 and author_id != 75:
        return {
            "status": "upgraded_quote_author",
            "quote_id": existing_quote.id,
            "new_author_id": author_id
        }

    # Case 2: Existing quote has a valid author
    return {
        "status": "duplicate_quote",
        "quote_id": existing_quote.id,
        "author_id": existing_quote.author_id
    }


class QuoteDuplicateException(Exception):
    def __init__(self, message, quote_id=None):
        self.quote_id = quote_id
        super().__init__(message)

#--------------- generation of dimensions and categories ------------------


# ALLOWED_EMOTIONS = ["love", "joy", "surprise", "anger", "sadness", "fear", "trust", "anticipation", "disgust", "relief", "pride", "serenity"]
ALLOWED_EMOTIONS = ["admiration", "amusement", "anger", "annoyance", "approval", "caring", "confusion", "curiosity", "desire", "disappointment",
                    "disapproval", "disgust", "embarrassment", "excitement", "fear", "gratitude", "grief", "joy", "love",
                    "nervousness", "optimism", "pride", "realization", "relief", "remorse", "sadness", "surprise"]



# ALLOWED_CATEGORIES = ["love", "relationships", "happiness", "well-being", "success", "motivation", "time", "space", "wisdom", "philosophy",
#                       "society", "politics", "faith", "spirituality", "education", "learning", "life",  "nature", "art", "culture",
#                       "physical_activity", "sports"]

ALLOWED_CATEGORIES = ["love", "relationships", "happiness", "friendships", "success", "motivation", "time", "space", "wisdom",
                      "society", "politics", "spirituality", "learning", "life",  "nature", "art", "culture", "sports", "humor"]


class Dimensions(BaseModel):
    polarity: str
    readability: str
    language: str    
    emotions: List[str]  
    categories: List[str]  # Set default to None


    # Validator to filter allowed categories
    @field_validator("categories", mode="before")
    def filter_categories(cls, value):
        if not isinstance(value, list):
            raise ValueError("Categories must be a list.")
        
        # Filter only allowed categories
        valid_categories = [category for category in value if category in ALLOWED_CATEGORIES]
        
        if not valid_categories:
            # raise ValueError("No valid categories provided. Allowed categories are: " + ", ".join(ALLOWED_CATEGORIES))
            valid_categories = ["miscellaneous"]
        
        return valid_categories
    
    # Validator to filter allowed categories
    @field_validator("emotions", mode="before")
    def filter_emotions(cls, value):
        if not isinstance(value, list):
            raise ValueError("Emotions must be a list.")
        
        # Filter only allowed categories
        valid_emotions = [emotion for emotion in value if emotion in ALLOWED_EMOTIONS]
        
        if not valid_emotions:
            # raise ValueError("No valid categories provided. Allowed categories are: " + ", ".join(ALLOWED_EMOTIONS))
            valid_emotions= ["unknown"]
        
        return valid_emotions    
    
  
  


def generate_response(quote):
    
    # Generate response using ChatOllama
    response_categorization = ollama.chat(
        model='categorization_llama3', 
        # format="json", 
        messages=[
            {
                'role': 'user',
                'content': f'Give me the dimensions of {quote} ',
            },
        ],
        # tools=[get_readability], # Actual function reference
        
        format=Dimensions.model_json_schema(),
        )  
    
    data = Dimensions.model_validate_json(response_categorization.message.content)  
    
    # print(f"{quote} \n=> {repr(data)}\n")
        

    
    return dict(data)