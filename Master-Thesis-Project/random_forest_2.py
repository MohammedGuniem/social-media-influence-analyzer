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

size_limit = 10

X = []
y = []
for record in data:
    for encoded_word in record['encoded_title']:
        X.append([encoded_word])
        y.append(record['encoded_topic'])

X = np.array(X)
y = np.array(y)

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
