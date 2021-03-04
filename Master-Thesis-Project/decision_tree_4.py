from classes.database_connectors.MongoDBConnector import MongoDBConnector
from sklearn.metrics import accuracy_score, precision_score, recall_score
from classes.crawling.RedditCrawlClass import RedditCrawler
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import KFold
from dotenv import load_dotenv
from datetime import date
import pandas as pd
import numpy as np
import string
import sys
import os

from classes.database_connectors.MongoDBConnector import MongoDBConnector
from classes.crawling.RedditCrawlClass import RedditCrawler
from sklearn.model_selection import train_test_split
from sklearn.neural_network import MLPClassifier
from sklearn.model_selection import KFold
from dotenv import load_dotenv
from datetime import date
import numpy as np
import string
import sys
import os

load_dotenv()

# Database connector
MongoDB_connection_string = os.environ.get('mongo_connnection_string')
mongo_db_connector = MongoDBConnector(MongoDB_connection_string)

data = mongo_db_connector.readFromDB(database_name="Topic_Detection", query={
}, single=False, collection_name="2021-03-03")

categories_words = {}
for record in data:
    for encoded_word in record['encoded_title']:
        category = record['encoded_topic']
        if category not in categories_words:
            categories_words[category] = []
        categories_words[category].append(encoded_word)

for k, v in categories_words.items():
    print(k, ": ", v[0:3])

sys.exit()


def find_common_words(lists):
    common = []
    for i in range(0, len(lists), 1):
        rest = []
        for l in lists[i+1:len(lists)]:
            rest += l
        current_common = list(set(lists[i]) & set(rest))
        common += current_common
    return list(set(common))


common = find_common_words(list(categories_words.values()))

for category, words in list(categories_words.items()):
    unique_list = []
    for word in words:
        if word not in common:
            unique_list.append(word)
    categories_words[category] = unique_list

X = []
y = []

for category, words in categories_words.items():
    for word in words:
        X.append([word])
        y.append(category)

X = np.array(X).astype(np.float32)
X = np.nan_to_num(X.astype(np.float32))
y = np.array(y)

# train and evaluate
kf = KFold(n_splits=5, shuffle=True, random_state=10)
for criterion in ['gini', 'entropy']:
    print("Decision Tree - {}".format(criterion))
    accuracy = []
    precision = []
    recall = []
    for train_index, test_index in kf.split(X):
        X_train, X_test = X[train_index], X[test_index]
        y_train, y_test = y[train_index], y[test_index]
        dt = DecisionTreeClassifier(criterion=criterion)
        dt.fit(X_train, y_train)
        y_pred = dt.predict(X_test)
        accuracy.append(accuracy_score(y_test, y_pred))
        precision.append(precision_score(y_test, y_pred, average='weighted'))
        recall.append(recall_score(y_test, y_pred, average='weighted'))
    print("accuracy:", np.mean(accuracy))
    print("precision:", np.mean(precision))
    print("recall:", np.mean(recall), '\n')
    print()


def get_letters_mapping():
    mapping = {}
    alphabet = list(string.printable)
    for letter in alphabet:
        mapping[letter] = ord(letter)
    return mapping


def encode(text):
    default_length = 10
    mapping = get_letters_mapping()
    text_array = text.lower().split(" ")
    encoded_array = []
    for word in text_array:
        encoded_word = ""
        for letter in word:
            if letter in mapping.keys():
                encoded_word += str(mapping[letter])
        if encoded_word == "":
            encoded_word = "0"
        encoded_array.append(float(encoded_word))
    return encoded_array


def predict(model, text):
    encoded_text = encode(text)
    sentence = []
    for encoded_word in encoded_text:
        sentence.append([encoded_word])

    sentence = np.array(sentence).astype(np.float32)
    sentence = np.nan_to_num(sentence.astype(np.float32))

    pre = model.predict(sentence)
    highest_frequency = 0
    most_frequent = 0
    for item in set(pre):
        item_frequency = list(pre).count(item)
        if item_frequency > highest_frequency:
            highest_frequency = item_frequency
            most_frequent = item

    return most_frequent


data = mongo_db_connector.readFromDB(database_name="Topic_Detection", query={
}, single=False, collection_name="2021-03-04")

correct = 0
wrong = 0
for record in data:
    prediction = predict(dt, record['title'])
    actual = record['encoded_topic']
    if actual == prediction:
        correct += 1
    else:
        wrong += 1

accuracy = correct / (correct+wrong)
failure = wrong / (correct+wrong)
print(accuracy)
print(failure)
