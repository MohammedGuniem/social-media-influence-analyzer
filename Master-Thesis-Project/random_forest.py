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
}, single=False, collection_name=str(date.today()))

size_limit = 10

X = []
y = []
for record in data:
    if len(record['encoded_title']) > size_limit:
        X.append(record['encoded_title'][0:size_limit])
    elif len(record['encoded_title']) < size_limit:
        r = record['encoded_title'] + \
            ((size_limit - len(record['encoded_title'])) * [0.0])
        X.append(r)
    else:
        X.append(record['encoded_title'])
    y.append(record['encoded_topic'])

X = np.array(X).astype(np.float32)
X = np.nan_to_num(X.astype(np.float32))
y = np.array(y)

"""
obama: 1,
usa: 2,
election: 3,
ronaldo: 4,
soccer: 5,
winner: 6,
funny: 7,
hilarious: 8
cool: 9
politics: 10,
football: 11,
comedy: 12
"""

"""
X = np.array([
    [1, 2.0, 3],
    [1, 2, 3],
    [4, 5, 6],
    [4, 5, 6],
    [7, 8, 9],
    [7, 8, 9]
])

y = np.array([10, 10, 11, 11, 12, 12])
"""

"""
    param_grid = {
        'n_estimators': [10, 25, 50, 75, 100],
    }
"""

# train and evaluate¨
kf = KFold(n_splits=5, shuffle=True)

mean_accuracy = []
for n in range(1, 101, 1):
    accuracy = []
    precision = []
    recall = []
    for train_index, test_index in kf.split(X):

        X_train, X_test = X[train_index], X[test_index]
        y_train, y_test = y[train_index], y[test_index]

        rf = RandomForestClassifier(random_state=123, n_estimators=n)
        rf.fit(X_train, y_train)

        y_pred = rf.predict(X_test)
        accuracy.append(accuracy_score(y_test, y_pred))
        precision.append(precision_score(y_test, y_pred, average='weighted'))
        recall.append(recall_score(y_test, y_pred, average='weighted'))

    print("n_estimators:", n)
    print("accuracy:", np.mean(accuracy))
    print("precision:", np.mean(precision))
    print("recall:", np.mean(recall), '\n')
    print()
    mean_accuracy.append(np.mean(accuracy))

statistics_methods.line_plot(x=range(1, 101, 1), y=mean_accuracy,
                             xlabel="n_estimators", ylabel="accuracy", legend="")
