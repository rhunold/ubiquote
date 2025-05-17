from prefect import task
from texts.quotes.models import Quote, Category

# from tasks.chatollama_quote5 import generate_response
from texts.quotes.utils import generate_response

@task
def enrich_quote_and_assign_categories(cleaned_text: str):
    dimensions_raw = generate_response(cleaned_text) 
    categories = []
    if "categories" in dimensions_raw:
        for cat_name in dimensions_raw["categories"]:
            cat, _ = Category.objects.get_or_create(
                title__iexact=cat_name.strip(), defaults={"title": cat_name}
            )
            categories.append(cat)

    # On retire les catégories du dict "dimensions"
    dimensions = {
        k: v for k, v in (dimensions_raw or {}).items() if k != "categories"
    }

    return dimensions, categories
