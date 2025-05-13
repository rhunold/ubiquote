from prefect import flow, task
from texts.quotes.models import Quote
from texts.quotes.utils import QuoteDuplicateChecker



@task
def check_for_duplicate_quote(text, incoming_author_id):
    checker = QuoteDuplicateChecker(text, incoming_author_id)
    is_dup, existing_quote = checker.is_duplicate()

    if not is_dup:
        return {"status": "no_duplicate"}

    # Duplication found
    if existing_quote.author_id == 75 and incoming_author_id != 75:
        return {
            "status": "upgrade_author",
            "quote_id": existing_quote.id,
            "new_author_id": incoming_author_id
        }

    return {
        "status": "duplicate_skip"
    }
        
# @flow
# def import_quotes_flow(quotes_to_import):
#     for item in quotes_to_import:
#         create_quote_if_not_duplicate.submit(item['text'], item['author_id'])
