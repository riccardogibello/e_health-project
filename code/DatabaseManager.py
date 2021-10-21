import re
import mysql
import mysql.connector


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
        print('LOL')
        # Rolling back in case of error
        conn.rollback()

    # Closing the connection
    conn.close()
    return result


def clear_database_data():
    do_query('', 'TRUNCATE TABLE category')
    do_query('', 'TRUNCATE TABLE app')


def insert_id_into_preliminary_db(app_id, from_dataset_flag=False):
    id_query = (
        "INSERT IGNORE INTO PRELIMINARY(app_id, from_dataset)"
        "VALUES (%s, %s)"
    )

    do_query((app_id, from_dataset_flag), id_query)


def delete_app_from_database(app_id):
    delete_query = (
        "DELETE FROM APP WHERE app_id = %s"
    )
    do_query((app_id,), delete_query)


def update_status_preliminary(app_id):
    update_query = (
        "UPDATE PRELIMINARY SET preliminary.check=TRUE WHERE app_id = %s"
    )
    do_query((app_id,), update_query)


def insert_app_into_db(application):
    insert_query = (
        "INSERT INTO APP(app_id, app_name, description, category, score, rating, category_id, developer_id, "
        "teacher_approved) "
        "VALUES (%s,%s,%s,%s,%s,%s,%s,%s, %s)"
    )

    query_values = (application.app_id,
                    application.title,
                    application.description,
                    application.category,
                    application.score,
                    application.ratings,
                    application.genre_id,
                    application.developer_id,
                    application.is_teacher_approved
                    )

    do_query(tuple_data=query_values, query=insert_query)


class DatabaseManager:
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
