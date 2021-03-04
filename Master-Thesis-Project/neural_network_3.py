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

min_length = len(list(categories_words.values())[0])
for category, words in categories_words.items():
    if len(words) < min_length:
        min_length = len(words)

print(min_length)

X = []
y = []

for category, words in categories_words.items():
    for word in words[0:min_length]:
        X.append([word])
        y.append(category)

X = np.array(X)
y = np.array(y)

# train and evaluate
scores = []
kf = KFold(n_splits=5, shuffle=True, random_state=10)
for train_index, test_index in kf.split(X):
    X_train, X_test = X[train_index], X[test_index]
    y_train, y_test = y[train_index], y[test_index]
    model = MLPClassifier(max_iter=1000)
    model.fit(X_train, y_train)
    scores.append(model.score(X_test, y_test))
score = np.mean(scores)
print(F"accuracy: {score}")
