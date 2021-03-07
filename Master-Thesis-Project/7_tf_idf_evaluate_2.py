from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from classes.database_connectors.MongoDBConnector import MongoDBConnector
from classes.statistics.Statistics import Statistics as statistics_methods
from sklearn.model_selection import KFold
from classes.tf_idf.TFIDF import TFIDF
from dotenv import load_dotenv
import numpy as np
import os

load_dotenv()

# Database connector
MongoDB_connection_string = os.environ.get('mongo_connnection_string')
mongo_db_connector = MongoDBConnector(MongoDB_connection_string)

docs = mongo_db_connector.readFromDB(database_name="Machine_Learning", query={
}, single=True, collection_name="Test_Topic_Detection")
del docs["_id"]

doc_counter = 0
train_features = []
test_features = []
train_labels = []
test_labels = []
for category, titles in docs.items():
    for title in titles:
        doc_counter += 1
        if doc_counter < 100:  # train subreddit 1 contains 100 titles
            train_features.append(title)
            train_labels.append(category)
        elif doc_counter < 200:  # test subreddit 2 contains 100 titles
            test_features.append(title)
            test_labels.append(category)
    doc_counter = 0

train_features = np.array(train_features)
train_labels = np.array(train_labels)

test_features = np.array(test_features)
test_labels = np.array(test_labels)
X_test = test_features
y_test = test_labels

X_train = train_features
y_train = train_labels

training_data = {}
for index in range(0, len(y_train), 1):
    category = y_train[index]
    if category in training_data:
        training_data[category].append(X_train[index])
    else:
        training_data[category] = [X_train[index]]
tf_idf = TFIDF(training_data)

y_classified = tf_idf.classify(X_test)

accuracy = accuracy_score(y_test, y_classified)
precision = precision_score(y_test, y_classified, zero_division=0,
                            average='weighted', labels=np.unique(y_test))
recall = recall_score(y_test, y_classified, zero_division=0,
                      average='weighted', labels=np.unique(y_test))
f1 = f1_score(y_test, y_classified, zero_division=0,
              average='weighted', labels=np.unique(y_test))

print(F"accuracy: {accuracy}")
print(F"precision: {precision}")
print(F"recall: {recall}")
print(F"F1-score: {f1}")
