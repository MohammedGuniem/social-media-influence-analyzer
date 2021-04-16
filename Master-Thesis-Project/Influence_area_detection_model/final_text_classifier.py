from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
from classes.database_connectors.MongoDBConnector import MongoDBConnector
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.linear_model import SGDClassifier
from sklearn.naive_bayes import MultinomialNB
from sklearn.model_selection import KFold
from sklearn.pipeline import Pipeline
from dotenv import load_dotenv
from datetime import date
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

today_date = str(date.today())

data = mongo_db_connector.readFromDB(database_name="Text_Classification_Training_Data", query={
}, single=True, collection_name=today_date)
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

print()
print("Small test")
test_titles = [
    {
        "title": "Tech giant invests 30 billions in renewable energy",
        "expected_topic_class": "economy"
    },
    {
        "title": "If only America could have short election cycles like near everywhere else",
        "expected_topic_class": "politic"
    },
    {
        "title": "100 days to go until Tokyo 2020",
        "expected_topic_class": "sport"
    },
    {
        "title": "Kroger Is Amassing A Robot Army To Battle Amazon, Walmart",
        "expected_topic_class": "technology"
    }
]
print("title, expected, predicted")
for record in test_titles:
    title = record['title']
    expected_topic_class = record['expected_topic_class']
    predicted_topic_class = text_clf.predict([title])
    print(F"{title}, {expected_topic_class}, {predicted_topic_class}")
