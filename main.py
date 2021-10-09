import database_handling_functions
import web_wining_functions
from database_handling_functions import *

if __name__ == '__main__':
    databaseHandler = DatabaseHandler()
    databaseHandler.setup_connection_data()

    web_wining_functions.find_available_categories()
