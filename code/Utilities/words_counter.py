from DataManagers.DatabaseManager import do_query as query
from nltk.corpus import stopwords

not_last = ['to', 'for', 'your', 'is', 'let', 'and', 'of', 'at', 'are', 'in', 'a', 'the', 's', 'b', '0', '1', '2', '3',
            '4', '5', '6', '7', '8', '9', 'it', 'as', 'how', 'i', 'or', 'they', 'will', 'having', 'not', '11', 'with',
            'that', 'by', 'while', 'dictionary']

banned = ['greek', 'arabic', 'italian', 'russian', 'german', 'english', 'japanese', 'chinese', 'czech', 'french',
          'hindi', 'dutch', 'lithuanian', 'malaysian', 'norwegian', 'slovak', 'thai', 'vietnamese', 'croatian',
          'afrikaans', 'hungarian', 'nepali', 'urdu', 'afrikaans', 'finnish', 'romanian', 'ukrainian', 'moldavian',
          'bulgarian',
          'telugu', 'danish', 'georgian', 'indonesian', 'nepali', 'polish', 'burmese', 'farsi', 'malayalam',
          'punjabi', 'bengali', 'tagalog', 'swahili', 'spanish', 'portuguese', 'b', 'tutotoons', 'ling', 'pdf', 'etc',
          'conversation', 'korean', 'khmer', 'schedule', 'records', 'notes', 'absent', 'marked', 'message',
          'messages', 'false', 'test', 'quiz', 'university', 'pay', 'fee', 'fees', 'tatoo', 'british', 'american',
          'ethical', 'hacking', 'cybersecurity', 'excuses', 'true', 'share', 'photo', 'photos', 'font', 'magaizne', 'm',
          'chat', 'guitar',
          'ukulele', 'piano', 'languages', 'language', 'quickly', 'brain', 'database', 'management', 'teachers',
          'teacher', 'youtube', 'download', 'girls', 'school', 'online', 'monitor', '0', '1', '2', '3',
          '4', '5', '6', '7', '8', '9', 'students', 'privacy', 'z', 'course', 'platform', 'rhymes', 'track', 'we',
          'without', 'com', 'dictionary', 'money', 'widget', 'albanian', 'swedish', 'review', 'transcription',
          'transcriptions', 'solving', 'knowledge', 'cool', ]


def response_tuple_to_list(tuples_list):
    result = []
    for result_tuple in tuples_list:
        result.append(result_tuple[0])
    return result


def filter_token(string):
    if string[0] == '-':
        return string[1:]
    else:
        return string


def order_dictionary_desc(dictionary):
    return {k: v for k, v in sorted(dictionary.items(), key=lambda item: item[1], reverse=True)}


def extract_bigrams(strings_list, dictionary):
    for string in strings_list:
        tokens = string.split()
        for i in range(1, len(tokens)):
            # if not (tokens[i - 1] in words or tokens[i] in words):
            # continue
            bigram = tokens[i - 1] + ' ' + tokens[i]
            if bigram in dictionary:
                dictionary[bigram] += 1
            else:
                dictionary[bigram] = 1


def extract_trigrams(strings_list, dictionary, words, bigrams):
    for string in strings_list:
        tokens = string.split()
        for i in range(2, len(tokens)):
            trigram = tokens[i - 2] + " " + tokens[i - 1] + " " + tokens[i]
            if trigram in dictionary:
                dictionary[trigram] += 1
            else:
                dictionary[trigram] = 1


def extract_fourgrams(strings_list, dictionary, unigrams, bigrams, trigrams):
    for string in strings_list:
        tokens = string.split()
        for i in range(3, len(tokens)):
            t_3 = tokens[i - 3]
            t_2 = tokens[i - 2]
            t_1 = tokens[i - 1]
            t = tokens[i]
            if t_3 in banned or t_2 in banned or t_1 in banned or t in banned or t in not_last:
                continue
            fourgram = tokens[i - 3] + ' ' + tokens[i - 2] + ' ' + tokens[i - 1] + ' ' + tokens[i]
            if fourgram in dictionary:
                dictionary[fourgram] += 1
            else:
                dictionary[fourgram] = 1


def write_dictionary_to_file(dictionary, file, limit=2):
    for key in dictionary:
        if dictionary[key] <= limit or not key:
            continue
        file.write(f"{dictionary[key]} | {key}\n")
        file.flush()


# serious_info = (serious_apps_descriptions, serious_dictionaries, serious_files)
# serious, bigrams, trigrams
def analyze_words(category, serious, bigrams, trigrams):
    category_name = category[0]
    category_data = category[1]
    descriptions_list = category_data[0]
    dictionaries = category_data[1]
    files = category_data[2]
    extract_unigrams(descriptions_list, dictionaries[0])
    print(f"Extracted unigrams for {category_name}")
    extract_bigrams(descriptions_list, dictionaries[1], serious)
    print(f"Extracted bigrams for {category_name}")
    extract_trigrams(descriptions_list, dictionaries[2], serious, bigrams)
    print(f"Extracted trigrams for {category_name}")
    extract_fourgrams(descriptions_list, dictionaries[3], serious, bigrams, trigrams)
    print(f"Extracted fourgrams for {category_name}")

    for index in range(len(dictionaries)):
        dictionaries[index] = order_dictionary_desc(dictionaries[index])
        write_dictionary_to_file(dictionaries[index], files[index])  # TODO insert limit if needed
    print(f"Exported {category_name} dictionaries to file")


def create_difference_dictionary(dictionary_1, dictionary_2, file):
    result_dictionary = {}
    for key in dictionary_1:
        if key in dictionary_2:
            continue
            # result_dictionary[key] = dictionary_1[key] / len(dictionary_1)/2 - dictionary_2[key] / len(dictionary_2)
        else:
            result_dictionary[key] = dictionary_1[key]

    order_dictionary_desc(result_dictionary)

    write_dictionary_to_file(result_dictionary, file)


if __name__ == '__main__':
    print()
