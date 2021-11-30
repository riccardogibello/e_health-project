import re
from numpy import arange
from DataManagers.DatabaseManager import create_connection


def extract_descriptions():
    query = "SELECT app_id, description " \
            "FROM app"
    id_desc_list = do_query('', query)

    return id_desc_list


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


def print_string(file, string):
    try:
        cnt = 0
        for c in string:
            file.write(c)
            if cnt == 100:
                cnt = 0
                file.write("\n")
                continue
            elif c == '\n':
                cnt = 0
                continue
            cnt = cnt + 1
        if cnt != 100:
            file.write("\n")
    except UnicodeEncodeError:
        pass


def print_original_string(file, string):
    try:
        for c in string:
            file.write(c)
        file.write("\n")
    except UnicodeEncodeError:
        pass


def sanitize_string(string):
    new_string = str(string.encode('ascii', errors='ignore').decode())
    new_string = re.sub(r"[\b]+", "", new_string)
    new_string = re.sub(r"[\t]+", "", new_string)
    new_string = re.sub(r"[\f]+", "", new_string)
    new_string = re.sub(r"[\r]+", "", new_string)
    new_string = re.sub(r"[\n]+", " ", new_string)
    new_string = re.sub(r"[ ]+", " ", new_string)
    return new_string


def update_description(a_id, desc):
    desc = sanitize_string(desc)
    query = "UPDATE app SET description = %s WHERE app_id = %s"
    do_query([desc, a_id], query)


def update_batch(off, bat_size, app_list, thread_n):
    print('Thread ' + str(thread_n) + 'started.\n')
    if off + bat_size > len(app_list):
        off = len(app_list)
    for i in range(int(off), int(off + bat_size), 1):
        el = app_list[i]
        app_id = el[0]
        description = el[1]

        update_description(app_id, description)
    print('Thread ' + str(thread_n) + 'ended.\n')


if __name__ == '__main__':
    '''id_description_list = extract_descriptions()
    f_out = open('./data/output/sanitized.txt', 'w')
    batch_size = 0.01 * len(id_description_list) // 1
    n_threads_max = int(len(id_description_list) // batch_size + 1)
    offset = 0
    thread_number = 0

    with ThreadPoolExecutor(max_workers=n_threads_max) as executor:
        while offset < len(id_description_list):
            executor.submit(update_batch, offset, batch_size, id_description_list, thread_number)
            offset = offset + batch_size
            thread_number = thread_number + 1'''

    f_in = open('./data/input_data/descr_test.txt', 'r')  # open a sample description not yet sanitized
    lines = f_in.readlines()
    sanitized_lines = []
    n_lines = len(lines)

    for line in lines:
        curr_sanitized_string = sanitize_string(line)
        # if the line did not contain only special characters (eliminated) and
        # \n, \b etc... (replaced with a blank space), then...
        if curr_sanitized_string != ' ':
            sanitized_lines.append(curr_sanitized_string)

    n_lines = len(sanitized_lines)
    new_sanitized_lines = []
    # if the description did not contain only a single line, then...
    if n_lines > 1:
        current_line = sanitized_lines[0]  # current line analyzed
        for i in arange(0, n_lines, 1):
            if i < n_lines - 1:
                next_line = sanitized_lines[i + 1]  # next line analyzed, used to check if it is the start of
                # a new sentence (initial upper case character)
            else:
                next_line = 'I'

            is_new_sentence = False
            # check if the next line begins with an upper character
            for char in next_line:
                if char == ' ':
                    continue
                if not char.isupper():
                    break
                else:
                    is_new_sentence = True
                    break

            last_char = current_line[len(current_line) - 2]
            # if the last character of the line is not a stop symbol (like full stop) and the new line starts with an
            # upper-case character, then it means that I had a sentence without the full stop, so add it
            if is_new_sentence and last_char not in '.?!:;,-':
                current_line = current_line + '.'
            new_sanitized_lines.append(current_line)
            current_line = next_line

    f_out = open('./data/input/descr_test_sanitized.txt', 'w')
    new_desc = ''
    for san_line in new_sanitized_lines:
        new_desc = new_desc + san_line

    new_desc = re.sub(r"[ ]+", " ", new_desc)  # sanitize possible residual multiple spaces
    f_out.write(new_desc)
