from django.core.management.base import BaseCommand
from texts.quotes.models import Quote
from django.db import models
import re


class Command(BaseCommand):
    help = 'Clean up quotes data'

    def handle(self, *args, **options):    
    # Remove duplicate text in quotes
        lastSeenId = float('-Inf') # https://stackoverflow.com/questions/34264710/what-is-the-point-of-floatinf-in-python
        rows = Quote.objects.all().order_by('text')

        for row in rows:
            if row.text == lastSeenId:
                row.delete() # We've seen this id in a previous row
            else: # New id found, save it and check future rows for duplicates.
                lastSeenId = row.text 
                
        # Add a cleaning reg ex in text field
        quotes = Quote.objects.all()

        for quote in quotes:
            cleaned_content = self.clean_content(quote.text, quote.lang)
            quote.text = cleaned_content
            quote.save()

        self.stdout.write(self.style.SUCCESS('Data cleaned successfully'))

    def clean_content(self, text, lang):
        if lang == 'fr':
            # French rules
            text = self.apply_french_rules(text)

        elif lang == 'en':
            # English rules
            text = self.apply_english_rules(text)

        # Common rules here if needed  for all languages
        
        # Remove 2 or more consecutive whitespace 
        text = re.sub(r'\s\s+', ' ', text)
        
        # before a  dot, remove a space if there is one
        re.sub(r'\s\.', '\.', text)
        
        # Rules to remove space if at the start and/or end of text.
        re.sub(r'^\s+|\s+(?=\.)|\s+$', '', text)
        
        # After a dot, put a space 
        # text = re.sub(r'\.(?!(\.\.\.))(\S)', r'. \2', text)
        
        # If there is no dot at the end,
        if not text.endswith('.'):
            text += '.'
            
        # The first letter of word after a . is a uppercased
        text = re.sub(r'\.(\s*)(\w)', lambda x: f'.{x.group(1)}{x.group(2).capitalize()}', text)            
            
        # The first letter of word after a ? is a uppercased
        text = re.sub(r'\?(\s*)(\w)', lambda x: f'?{x.group(1)}{x.group(2).capitalize()}', text)
            
     

        return text
    


    def apply_french_rules(self, text):
        
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
        
        # remove extra space between a word and a comma
        # text = re.sub(r'(\w)(\s),', r'\1,', text)


        # Règle : Guillemets français
        # text = re.sub(r'"(.*?)"', r'«\1»', text)

        # Ajouter d'autres règles françaises ici si nécessaire

        
        # Add more French rules here if needed

        return text

    def apply_english_rules(self, text):
        # Example English rule: Insert your English-specific rule here // Maybe I can use it to switch some issue with author name (plato/platon) ?
        # For example, replace all occurrences of 'color' with 'colour'  
        text = re.sub(r'\bcolor\b', 'colour', text, flags=re.IGNORECASE)

        # Add more English rules here if needed

        return text
                
