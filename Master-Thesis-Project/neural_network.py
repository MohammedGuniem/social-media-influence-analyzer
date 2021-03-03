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
}, single=False, collection_name=str(date.today()))

words_lengths = []
size_limit = 10
X = []
y = []
for record in data:
    words_lengths.append(len(record['encoded_title']))
    if len(record['encoded_title']) > size_limit:
        X.append(record['encoded_title'][0:size_limit])
    elif len(record['encoded_title']) < size_limit:
        r = record['encoded_title'] + \
            ((size_limit - len(record['encoded_title'])) * [0])
        X.append(r)
    else:
        X.append(record['encoded_title'])
    y.append(record['encoded_topic'])

print(F"average word length {sum(words_lengths)/len(words_lengths)}")

X = np.array(X)
y = np.array(y)

words_num = 0
max_accuracy = 0
for size_limit in [size_limit]:
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
    print(F"size_limit: {size_limit} accuracy: {score}")

    if max_accuracy < score:
        max_accuracy = score
        words_num = size_limit

print(F"max at: size_limit: {words_num} accuracy: {max_accuracy}")

"""
predictions = mlp.predict(X_test)
print(F"expected: {y_test[0]}")
print(F"got: {decode_category(predictions[0])}")
"""
"""
X = np.array([
    encode("obama usa election"),
    encode("ronaldo soccer winner"),
    encode("funny hilarious cool"),
    encode("funny hilarious cool")
])

y = np.array([encode_category("politics"), encode_category("football"),
              encode_category("comedy"), encode_category("comedy")])
"""
