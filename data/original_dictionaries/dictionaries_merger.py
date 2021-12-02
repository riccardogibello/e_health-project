import os
import numpy as np
import re

if __name__ == '__main__':
    category_word_list = {}
    for i in np.arange(start=1, stop=8, step=1):
        old_directory_path = next(os.walk('{}/'.format(str(i))))
        file_names_list = old_directory_path[2]
        old_directory_path = os.path.join(str(i))

        # print(file_names_list)

        for file_name in file_names_list:
            word_list = category_word_list.get(file_name)
            if not word_list:
                word_list = ['\n']
            length_word_list = len(word_list)

            file_name_path = os.path.join(old_directory_path, file_name)
            input_file = open(file_name_path, 'r')

            file_word_list = input_file.readlines()
            i = 0
            for new_word in file_word_list:
                if re.search("^--.*--$", new_word):
                    continue
                new_word = new_word.lower()
                # print('For file ' + file_name + ' found ' + new_word + '.\n')
                for word in word_list:
                    if word == new_word:
                        break
                    elif i == length_word_list - 1:
                        word_list.append(new_word)
                        # print('For file ' + file_name + ' added ' + new_word + '.\n')
                    i = i + 1
                i = 0

            category_word_list.__setitem__(file_name, word_list)

    path_ = os.path.join('MERGED_DICTIONARIES/')
    os.makedirs(path_, exist_ok=True)

    # print(category_word_list.keys())
    for file_name in category_word_list.keys():
        new_file_path = os.path.join('MERGED_DICTIONARIES/', str(file_name))
        out_file = open(new_file_path, 'w')
        word_list = category_word_list.get(file_name)
        for word in word_list:
            if word == '\n':
                continue
            out_file.write(word)