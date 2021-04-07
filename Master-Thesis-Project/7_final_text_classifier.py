from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
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
import sys
import os

load_dotenv()

# featuresbase connector
mongo_db_host = os.environ.get('mongo_db_host')
mongo_db_port = os.environ.get('mongo_db_port')
mongo_db_user = os.environ.get('mongo_db_user')
mongo_db_pass = os.environ.get('mongo_db_pass')
mongo_db_connector = MongoDBConnector(
    host=mongo_db_host, port=int(mongo_db_port), user=mongo_db_user, passowrd=mongo_db_pass)

data = mongo_db_connector.readFromDB(database_name="Text_Classification_Training_Data", query={
}, single=True, collection_name="2021-03-31")
del data["_id"]

data = data["training_data"]
random.seed(99)
random.shuffle(data)
data = pd.DataFrame(data)
features = (data["title"]).to_numpy()
labels = (data["label"]).to_numpy()

text_clf = Pipeline([
    ('vect', CountVectorizer(ngram_range=(1, 2))),
    ('tfidf', TfidfTransformer(use_idf=True)),
    ('clf', SGDClassifier(alpha=0.001, random_state=99)),
])

"""
('clf', MultinomialNB()),
"""

training_percentage = 0.8
testing_percentage = 0.2
X_train, X_test = list(features[:int(training_percentage*len(features))]
                       ), list(features[int(testing_percentage*len(features)):])
y_train, y_test = list(labels[:int(training_percentage*len(features))]
                       ), list(labels[int(testing_percentage*len(features)):])

text_clf.fit(X_train, y_train)
y_pred = text_clf.predict(X_test)

print(classification_report(y_test, y_pred, target_names=list(set(labels))))

print(confusion_matrix(y_test, y_pred))
