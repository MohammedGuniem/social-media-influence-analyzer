from classes.database_connectors.MongoDBConnector import MongoDBConnector
from classes.crawling.RedditCrawlClass import RedditCrawler
from sklearn.model_selection import train_test_split
from sklearn.neural_network import MLPClassifier
from dotenv import load_dotenv
from datetime import date
import numpy as np
import string
import sys
import os

load_dotenv()

# prepare


def get_letters_mapping():
    mapping = {}
    alphabet = list(string.printable)
    for letter in alphabet:
        mapping[letter] = ord(letter)
    return mapping


def get_category_mapping():
    to_number = {
        "politics": 1,
        "sport": 2,
        "comedy": 3
    }
    to_text = {
        1: "politics",
        2: "sport",
        3: "comedy"
    }
    return to_number, to_text


def encode_category(category):
    to_number, _ = get_category_mapping()
    return to_number[category]


def decode_category(number):
    _, to_text = get_category_mapping()
    return to_text[number]


def encode(text):
    default_length = 100
    mapping = get_letters_mapping()
    encoded_array = []
    for letter in text:
        if letter in mapping.keys():
            encoded_array.append(mapping[letter])

    if len(encoded_array) > default_length:
        encoded_array = encoded_array[0:default_length]
    else:
        encoded_array = encoded_array + \
            ([0] * (default_length - len(encoded_array)))
    return encoded_array


def decode(encoded_array):
    text = ""
    for encoded_letter in encoded_array:
        text += chr(encoded_letter)
    return text


# Database connector
MongoDB_connection_string = os.environ.get('mongo_connnection_string')
mongo_db_connector = MongoDBConnector(MongoDB_connection_string)

data = mongo_db_connector.readFromDB(database_name="Topic_detection", query={
}, single=False, collection_name=str(date.today()))

size_limit = 50

words_num = 0
max_accuracy = 0
for size_limit in range(90, 100, 1):
    X = []
    y = []
    for record in data:
        if len(record['encoded_title']) > size_limit:
            X.append(record['encoded_title'][0:size_limit])
        elif len(record['encoded_title']) < size_limit:
            r = record['encoded_title'] + \
                ((size_limit - len(record['encoded_title'])) * [0])
            X.append(r)
        else:
            X.append(record['encoded_title'])
        y.append(record['encoded_topic'])

    X = np.array(X)
    y = np.array(y)

    # train and evaluate
    X_train, X_test, y_train, y_test = train_test_split(X, y, random_state=2)
    mlp = MLPClassifier(max_iter=1000)

    mlp.fit(X_train, y_train)
    score = mlp.score(X_test, y_test)
    print(F"size_limit: {size_limit} accuracy: {score}")

    if max_accuracy < score:
        max_accuracy = score
        words_num = size_limit

print(F"max at: size_limit: {words_num} accuracy: {max_accuracy}")

"""
predictions = mlp.predict(X_test)
print(F"expected: {y_test[0]}")
print(F"got: {decode_category(predictions[0])}")
"""
"""
X = np.array([
    encode("obama usa election"),
    encode("ronaldo soccer winner"),
    encode("funny hilarious cool"),
    encode("funny hilarious cool")
])

y = np.array([encode_category("politics"), encode_category("football"),
              encode_category("comedy"), encode_category("comedy")])
"""
