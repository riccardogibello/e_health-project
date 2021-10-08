import re
import mysql
import mysql.connector


def setup_connection_data():
    data = []
    try:
        fp = open('./data/connection_data/data.txt', 'r')
        data = fp.readlines()
    except FileNotFoundError:
        if not data:
            data.append(input('Insert the user you have used in MySql setup:\n'))
            data.append(input('Insert the related password you have used in MySql setup:\n'))
            data.append('127.0.0.1')
            data.append(input('Insert the database name you have used in MySql setup:\n'))
            fo = open('./data/connection_data/data.txt', "w")
            for datum in data:
                fo.write(datum + '\n')

    sanitized_data = []
    for datum in data:
        sanitized_data.append(re.sub('\n', '', datum, flags=re.IGNORECASE))
    print(sanitized_data)


def insert_user():
    # establishing the connection
    conn = create_connection()

    # Creating a cursor object using the cursor() method
    cursor = conn.cursor()

    # Preparing SQL query to INSERT a record into the database.
    insert_stmt = (
        "INSERT INTO USER(userid, name, surname, username, password)"
        "VALUES (%s, %s, %s, %s, %s)"
    )
    data = (7, 'Riccardo', 'Gibello', 'Ric', 'Abs')

    try:
        # Executing the SQL command
        cursor.execute(insert_stmt, data)

        # Commit your changes in the database
        conn.commit()
    except EnvironmentError:
        # Rolling back in case of error
        conn.rollback()

    print("Data inserted")

    # Closing the connection
    conn.close()


def insert_tuple(tuple_data, query):
    # establishing the connection
    conn = create_connection()

    # Creating a cursor object using the cursor() method
    cursor = conn.cursor()

    try:
        # Executing the SQL command
        cursor.execute(query, tuple_data)

        # Commit your changes in the database
        conn.commit()
    except EnvironmentError:
        # Rolling back in case of error
        conn.rollback()

    print("Data inserted")

    # Closing the connection
    conn.close()


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
