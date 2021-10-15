import play_scraper
import DatabaseManager


def find_available_categories():
    categories = play_scraper.categories()

    for first_key, category in categories.items():
        data = []
        for second_key, category_datum in category.items():
            if second_key != 'url':
                data.append(category_datum)
        query = (
            "INSERT INTO CATEGORY(category_name, category_id)"
            "VALUES (%s, %s)"
        )
        DatabaseManager.do_query(data, query)
