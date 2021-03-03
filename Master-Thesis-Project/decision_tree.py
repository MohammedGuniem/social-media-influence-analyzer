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
