import re
import mysql
import mysql.connector


def retrieve_columns_names():
    query = "SELECT COLUMNS.COLUMN_NAME FROM information_schema.COLUMNS WHERE table_schema='projectdatabase' " \
            "and TABLE_NAME='app_features' ORDER BY ORDINAL_POSITION"
    result = do_query('', query)
    col_names = []
    for el in result:
        name = str(el[0])
        col_names.append(name)
    return col_names


def retrieve_columns_names_given_table(table_name):
    query = "SELECT COLUMNS.COLUMN_NAME FROM information_schema.COLUMNS " \
            "WHERE TABLE_NAME=%s AND table_schema='projectdatabase' " \
            "ORDER BY ORDINAL_POSITION"
    result = do_query((table_name,), query)
    col_names = []
    for el in result:
        name = str(el[0])
        col_names.append(name)
    return col_names


def create_connection():
    # retrieving from /data/connection_data/data.txt all the needed information for establishing a connection
    fp = open('./data/connection_data/data.txt', 'r')
    data = fp.readlines()
    sanitized_data = []
    for datum in data:
        sanitized_data.append(re.sub('\n', '', datum, flags=re.IGNORECASE))

    # establishing the connection
    return mysql.connector.connect(
        user=sanitized_data[0], password=sanitized_data[1], host=sanitized_data[2], database=sanitized_data[3])


def do_query(tuple_data, query):
    # establishing the connection
    conn = create_connection()

    # Creating a cursor object using the cursor() method
    cursor = conn.cursor()
    result = []

    try:
        # Executing the SQL command
        cursor.execute(query, tuple_data)
        result = cursor.fetchall()
        # Commit your changes in the database
        conn.commit()
    except EnvironmentError:
        # Rolling back in case of error
        conn.rollback()

    # Closing the connection
    conn.close()
    return result


def do_multiple_queries(dict_query_paramstuple):
    # establishing the connection
    conn = create_connection()

    # Creating a cursor object using the cursor() method
    cursor = conn.cursor()
    query_result_dict = {}

    try:
        # Executing the SQL command
        for query in dict_query_paramstuple.keys():
            params = dict_query_paramstuple.get(query)
            cursor.execute(query, params)
            result = cursor.fetchall()
            query_result_dict.__setitem__(query, result)
        # Commit your changes in the database
        conn.commit()
    except EnvironmentError:
        # Rolling back in case of error
        conn.rollback()

    # Closing the connection
    conn.close()
    return query_result_dict


def multiple_query(tuple_list, query):
    # establishing the connection
    conn = create_connection()

    # Creating a cursor object using the cursor() method
    cursor = conn.cursor()
    result = []

    try:
        # Executing the SQL command
        cursor.executemany(query, tuple_list)
        result = cursor.fetchall()
        # Commit your changes in the database
        conn.commit()
    except EnvironmentError:
        # Rolling back in case of error
        conn.rollback()

    # Closing the connection
    conn.close()
    return result


def clear_table(table_name):
    do_query('', 'TRUNCATE TABLE ' + table_name)


def insert_id_into_preliminary_db(app_id, from_dataset_flag=False):
    id_query = (
        "INSERT IGNORE INTO PRELIMINARY(app_id, from_dataset)"
        "VALUES (%s, %s)"
    )

    do_query((app_id, from_dataset_flag), id_query)


def delete_id_from_preliminary_db(app_id):
    remove_query = (
        "DELETE FROM preliminary WHERE app_id = %s"
    )
    do_query((app_id,), remove_query)


def delete_app_from_labeled_app(app_id):
    do_query((app_id,), "DELETE FROM labeled_app WHERE app_id = %s")


def delete_app_from_database(app_id):
    delete_query = (
        "DELETE FROM APP WHERE app_id = %s"
    )
    do_query((app_id,), delete_query)


def get_apps_from_preliminary():
    get_query = (
        "SELECT app_id FROM preliminary"
    )
    return do_query((), get_query)


def update_status_preliminary(app_id):
    update_query = (
        "UPDATE PRELIMINARY SET preliminary.check=TRUE WHERE app_id = %s"
    )
    do_query((app_id,), update_query)


def insert_app_into_db(application):
    insert_query = (
        "INSERT IGNORE INTO APP(app_id, app_name, description, category_id, score, rating, installs,"
        " developer_id, last_update, content_rating, teacher_approved) "
        "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
    )

    query_values = (application.app_id,
                    application.title,
                    application.description,
                    application.genre_id,
                    application.score,
                    application.ratings,
                    application.min_installs,
                    application.developer_id,
                    application.updated,
                    application.content_rating,
                    application.teacher_approved
                    )

    do_query(tuple_data=query_values, query=insert_query)


def insert_developer(developer_id, developer_name):
    if developer_id and developer_name:
        do_query((developer_id, developer_name), (
            "INSERT IGNORE INTO developer(id, name) "
            "VALUES (%s, %s)"
        ))


def mark_as_non_existing(app_id):
    do_query((app_id,), "UPDATE preliminary SET preliminary.existing=FALSE WHERE app_id = %s")


class DatabaseManager:
    """
    This class is mainly intended to handle the communication between the python code and the MySQL database.
    The functions defined above are some utilities used, for example, to retrieve the names of the columns of some
    specific tables in the database, to clear some specified tables or to perform single / multiple queries.
    """
    __connection_data = []

    def get_connection_data(self):
        return self.__connection_data

    def setup_connection_data(self):
        data = []
        try:
            fp = open('./data/connection_data/data.txt', 'r')
            data = fp.readlines()
        except FileNotFoundError:
            data.append(input('Insert the user you have used in MySql setup:\n'))
            data.append(input('Insert the related password you have used in MySql setup:\n'))
            data.append('127.0.0.1')
            data.append(input('Insert the database name you have used in MySql setup:\n'))
            fo = open('./data/connection_data/data.txt', "w")
            for datum in data:
                fo.write(datum + '\n')

        for datum in data:
            self.__connection_data.append(re.sub('\n', '', datum, flags=re.IGNORECASE))
