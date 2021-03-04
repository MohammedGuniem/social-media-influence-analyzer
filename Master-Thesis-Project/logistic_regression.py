from classes.database_connectors.MongoDBConnector import MongoDBConnector
from sklearn.metrics import accuracy_score, precision_score, recall_score
from classes.crawling.RedditCrawlClass import RedditCrawler
from sklearn.linear_model import LogisticRegression
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
accuracy = []
precision = []
recall = []
for train_index, test_index in kf.split(X):
    X_train, X_test = X[train_index], X[test_index]
    y_train, y_test = y[train_index], y[test_index]
    lr = LogisticRegression(solver="lbfgs", max_iter=99999999999999)
    lr.fit(X_train, y_train)
    accuracy.append(lr.score(X_test, y_test))
    y_pred = lr.predict(X_test)
    precision.append(precision_score(
        y_test, y_pred, average='weighted', labels=np.unique(y_pred)))
    recall.append(recall_score(y_test, y_pred,
                               average='weighted', labels=np.unique(y_pred)))
print("accuracy:", np.mean(accuracy))
print("precision:", np.mean(precision))
print("recall:", np.mean(recall), '\n')
print()
