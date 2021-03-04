from classes.statistics.Statistics import Statistics as statistics_methods
from classes.database_connectors.MongoDBConnector import MongoDBConnector
from sklearn.metrics import accuracy_score, precision_score, recall_score
from classes.crawling.RedditCrawlClass import RedditCrawler
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import KFold
from dotenv import load_dotenv
from datetime import date
import pandas as pd
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


def run_random_forest(splits, n_estimators):
    accuracy = []
    precision = []
    recall = []
    for train_index, test_index in kf.split(X):
        X_train, X_test = X[train_index], X[test_index]
        y_train, y_test = y[train_index], y[test_index]

        rf = RandomForestClassifier(
            random_state=123, n_estimators=n_estimators)
        rf.fit(X_train, y_train)

        y_pred = rf.predict(X_test)
        accuracy.append(accuracy_score(y_test, y_pred))
        precision.append(precision_score(y_test, y_pred, average='weighted'))
        recall.append(recall_score(y_test, y_pred, average='weighted'))
    return accuracy, precision, recall


mean_accuracy = []
mean_precision = []
mean_recall = []
n_estimators_range_list = range(1, 101, 10)
kf = KFold(n_splits=5, shuffle=True)
for n in n_estimators_range_list:
    accuracy, precision, recall = run_random_forest(splits=kf, n_estimators=n)
    mean_accuracy.append(np.mean(accuracy))
    mean_precision.append(np.mean(precision))
    mean_recall.append(np.mean(recall))

print("mean accuracy:", np.mean(mean_accuracy))
print("mean precision:", np.mean(mean_precision))
print("mean recall:", np.mean(mean_recall), '\n')
print()

statistics_methods.line_plot(x=n_estimators_range_list, y=mean_accuracy,
                             xlabel="n_estimators", ylabel="accuracy", legend="")
