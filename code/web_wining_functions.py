import play_scraper
import database_handling_functions


def find_available_categories():
    categories = play_scraper.categories()

    for key, category in categories.items():
        data = []
        for key, cateogry_datum in category.items():
            if key != 'url':
                data.append(cateogry_datum)
        query = (
            "INSERT INTO CATEGORY(category_name, category_id)"
            "VALUES (%s, %s)"
        )
        database_handling_functions.insert_tuple(data, query)
