import database_handling_functions
import web_wining_functions
from database_handling_functions import *

if __name__ == '__main__':
    database_handling_functions.setup_connection_data()

    # read_dataset()
    web_wining_functions.find_available_categories()
