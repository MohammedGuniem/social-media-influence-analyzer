import sys
for path in sys.path:
    if "Influence_area_detection_model" in path:
        main_project_path = "\\".join(path.split("\\")[0:-1])
        sys.path.append(main_project_path)
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from classes.database_connectors.MongoDBConnector import MongoDBConnector
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.linear_model import SGDClassifier
from sklearn.naive_bayes import MultinomialNB
from sklearn.model_selection import KFold
from sklearn.pipeline import Pipeline
from dotenv import load_dotenv
import pandas as pd
import numpy as np
import random
import os

load_dotenv()
 
# Mongo DB Database Connector
mongo_db_connector = MongoDBConnector(
    host=os.environ.get('mongo_db_host'), 
    port=int(os.environ.get('mongo_db_port')), 
    user=os.environ.get('mongo_db_user'), 
    passowrd=os.environ.get('mongo_db_pass')
)

data = mongo_db_connector.readFromDB(database_name="Test_New_Training_Data", query={
}, single=True, collection_name="2021-04-21")
del data["_id"]

data = data["training_data"]
random.seed(99)
random.shuffle(data)
data = pd.DataFrame(data)
features = (data["title"]).to_numpy()
labels = (data["label"]).to_numpy()

text_clf = Pipeline([
    ('vect', CountVectorizer()),
    ('tfidf', TfidfTransformer()),
    ('clf', SGDClassifier()),
])

"""
('clf', MultinomialNB()),
"""

accuracy_scores = []
precision_scores = []
recall_scores = []
f1_scores = []


kf = KFold(n_splits=5, shuffle=True, random_state=99)
for train_index, test_index in kf.split(features):
    X_train, X_test = list(features[train_index]), list(features[test_index])
    y_train, y_test = list(labels[train_index]), list(labels[test_index])

    text_clf.fit(X_train, y_train)
    y_pred = text_clf.predict(X_test)

    accuracy = accuracy_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred, zero_division=0,
                                average='weighted', labels=np.unique(y_test))
    recall = recall_score(y_test, y_pred, zero_division=0,
                          average='weighted', labels=np.unique(y_test))
    f1 = f1_score(y_test, y_pred, zero_division=0,
                  average='weighted', labels=np.unique(y_test))

    accuracy_scores.append(accuracy)
    precision_scores.append(precision)
    recall_scores.append(recall)
    f1_scores.append(f1)

print(F"accuracy: {np.mean(accuracy_scores)}")
print(F"precision: {np.mean(precision_scores)}")
print(F"recall: {np.mean(recall_scores)}")
print(F"F1-score: {np.mean(f1_scores)}")
