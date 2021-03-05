
from classes.statistics.Statistics import Statistics as statistics_methods
from classes.database_connectors.MongoDBConnector import MongoDBConnector
from sklearn.metrics import accuracy_score, precision_score, recall_score
from classes.crawling.RedditCrawlClass import RedditCrawler
from sklearn.ensemble import RandomForestClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.preprocessing import OneHotEncoder
from sklearn.preprocessing import LabelEncoder
from dotenv import load_dotenv
from datetime import date
import numpy as np
import statistics
import base64
import sys
import os


load_dotenv()

# Database connector
MongoDB_connection_string = os.environ.get('mongo_connnection_string')
mongo_db_connector = MongoDBConnector(MongoDB_connection_string)

train_data = mongo_db_connector.readFromDB(database_name="Train_Topic_Detection", query={
}, single=True, collection_name="2021-03-05")

test_data = mongo_db_connector.readFromDB(database_name="Test_Topic_Detection", query={
}, single=True, collection_name="2021-03-05")

# preparing training data
train_X = []
train_y = []
del train_data["_id"]
for category, words in train_data.items():
    train_X += words
    train_y += [category] * len(words)
enc = OneHotEncoder(handle_unknown='ignore')
enc.fit(train_X)
X_train = enc.transform(train_X).toarray()
label_enc = LabelEncoder()
label_enc.fit(train_y)
y_train = label_enc.transform(train_y)

# preparing test data
test_X = []
test_y = []
del test_data["_id"]
for category, titles in test_data.items():
    test_X += titles
    test_y += [category] * len(titles)
y_test = label_enc.transform(test_y)


def predict(X_test, encoder, model):
    predictions = []
    for title in X_test:
        words = []
        for word in title.split(" "):
            words.append([word])
        encoded_words = encoder.transform(words).toarray()
        title_predictions = model.predict(encoded_words)
        predictions.append(statistics.mode(title_predictions))
    return predictions


# train and evaluate
print("\n----------Decision Tree Evaluation----------")
for criterion in ['gini', 'entropy']:
    print("Decision Tree - {}".format(criterion))
    accuracy = []
    precision = []
    recall = []
    dt = DecisionTreeClassifier(criterion=criterion)
    dt.fit(X_train, y_train)
    #y_pred = dt.predict(X_test)
    y_pred = predict(test_X, enc, dt)
    accuracy.append(accuracy_score(y_test, y_pred))
    precision.append(precision_score(
        y_test, y_pred, average='weighted', labels=np.unique(y_pred)))
    recall.append(recall_score(y_test, y_pred,
                               average='weighted', labels=np.unique(y_pred)))
    print("accuracy:", np.mean(accuracy))
    print("precision:", np.mean(precision))
    print("recall:", np.mean(recall), '\n')
    print()

print("\n----------Random Forest Evaluation----------")


def run_random_forest(n_estimators):
    accuracy = []
    precision = []
    recall = []
    rf = RandomForestClassifier(random_state=123, n_estimators=n_estimators)
    rf.fit(X_train, y_train)
    y_pred = predict(test_X, enc, rf)
    accuracy.append(accuracy_score(y_test, y_pred))
    precision.append(precision_score(
        y_test, y_pred, average='weighted', labels=np.unique(y_pred)))
    recall.append(recall_score(y_test, y_pred,
                               average='weighted', labels=np.unique(y_pred)))
    return accuracy, precision, recall


mean_accuracy = []
mean_precision = []
mean_recall = []
n_estimators_range_list = range(1, 101, 10)
for n in n_estimators_range_list:
    accuracy, precision, recall = run_random_forest(n_estimators=n)
    mean_accuracy.append(np.mean(accuracy))
    mean_precision.append(np.mean(precision))
    mean_recall.append(np.mean(recall))

print("mean accuracy:", np.mean(mean_accuracy))
print("mean precision:", np.mean(mean_precision))
print("mean recall:", np.mean(mean_recall), '\n')
print()

statistics_methods.line_plot(x=n_estimators_range_list, y=mean_accuracy,
                             xlabel="n_estimators", ylabel="accuracy", legend="")

print("\n----------Neural Network Evaluation----------")
mean_accuracy = []
mean_precision = []
mean_recall = []
nn = MLPClassifier(max_iter=1000)
nn.fit(X_train, y_train)
y_pred = predict(test_X, enc, nn)
mean_accuracy.append(accuracy_score(y_test, y_pred))
mean_precision.append(precision_score(
    y_test, y_pred, average='weighted', labels=np.unique(y_pred)))
mean_recall.append(recall_score(
    y_test, y_pred, average='weighted', labels=np.unique(y_pred)))
print("mean accuracy:", np.mean(mean_accuracy))
print("mean precision:", np.mean(mean_precision))
print("mean recall:", np.mean(mean_recall), '\n')
