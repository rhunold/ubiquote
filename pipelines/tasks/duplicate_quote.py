from prefect import flow, task
from texts.quotes.models import Quote
from texts.quotes.utils import QuoteDuplicateChecker
# from texts.quotes.utils import check_and_handle_duplicate_quote


@task
def check_for_duplicate_quote(cleaned_text, incoming_author_id):

    checker = QuoteDuplicateChecker(cleaned_text, incoming_author_id)
    is_dup, existing_quote = checker.is_duplicate()

    if not is_dup:
        return {"status": "not_duplicate"}

    # Duplication found
    if existing_quote.author_id == 75 and incoming_author_id != 75:
        return {
            "status": "upgraded_quote_author",
            "quote_id": existing_quote.id,
            "new_author_id": incoming_author_id
        }
        # print(is_dup)
        # print(result)
        # return result
        
    # if existing_quote.author_id == incoming_author_id and  :
    #     return {
    #     "status": "duplicate_quote"
    #     }        

    return {
        "status": "duplicate_quote"
    }


