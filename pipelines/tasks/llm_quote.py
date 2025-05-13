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

# @task
# def enrich_quote_and_assign_categories(quote_id: int):
#     quote = Quote.objects.get(id=quote_id)
#     insights = generate_response(quote.text)
#     print(insights)

#     if not insights:
#         return None

#     # Ajoute dans JSON
#     quote.dimensions = {**(quote.dimensions or {}), **{
#         k: v for k, v in insights.items() if k != "categories"
#     }}
#     quote.save(update_fields=["dimensions"])

#     # Gestion des catégories (ManyToMany)
#     if "categories" in insights:
#         for cat_name in insights["categories"]:
#             cat, _ = Category.objects.get_or_create(title__iexact=cat_name.strip(), defaults={"title": cat_name})
#             quote.categories.add(cat)

#     print(f"✅ Quote {quote_id} enrichie avec catégories.")
#     return quote.id
