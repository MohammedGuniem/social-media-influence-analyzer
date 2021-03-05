
from classes.statistics.Statistics import Statistics as statistics_methods
from classes.database_connectors.MongoDBConnector import MongoDBConnector
from sklearn.metrics import accuracy_score, precision_score, recall_score
from classes.crawling.RedditCrawlClass import RedditCrawler
from sklearn.ensemble import RandomForestClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.preprocessing import OneHotEncoder
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import KFold
from dotenv import load_dotenv
from datetime import date
import numpy as np
import base64
import sys
import os


load_dotenv()

# Database connector
MongoDB_connection_string = os.environ.get('mongo_connnection_string')
mongo_db_connector = MongoDBConnector(MongoDB_connection_string)

data = mongo_db_connector.readFromDB(database_name="Train_Topic_Detection", query={
}, single=True, collection_name="2021-03-05")

X = []
y = []

del data["_id"]
for category, words in data.items():
    X += words
    y += [category] * len(words)

enc = OneHotEncoder(handle_unknown='ignore')
enc.fit(X)

label_enc = LabelEncoder()
label_enc.fit(y)

X = enc.transform(X).toarray()
y = label_enc.transform(y)

print(len(X))
print(len(y))

# train and evaluate
kf = KFold(n_splits=5, shuffle=True, random_state=10)
print("\n----------Decision Tree Evaluation----------")
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
        precision.append(precision_score(
            y_test, y_pred, average='weighted', labels=np.unique(y_pred)))
        recall.append(recall_score(y_test, y_pred,
                                   average='weighted', labels=np.unique(y_pred)))
    print("accuracy:", np.mean(accuracy))
    print("precision:", np.mean(precision))
    print("recall:", np.mean(recall), '\n')
    print()

# sys.exit(0)

print("\n----------Random Forest Evaluation----------")


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
    accuracy, precision, recall = run_random_forest(
        splits=kf, n_estimators=n)
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
for train_index, test_index in kf.split(X):
    X_train, X_test = X[train_index], X[test_index]
    y_train, y_test = y[train_index], y[test_index]
    model = MLPClassifier(max_iter=1000)
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    mean_accuracy.append(accuracy_score(y_test, y_pred))
    mean_precision.append(precision_score(
        y_test, y_pred, average='weighted', labels=np.unique(y_pred)))
    mean_recall.append(recall_score(
        y_test, y_pred, average='weighted', labels=np.unique(y_pred)))
print("mean accuracy:", np.mean(mean_accuracy))
print("mean precision:", np.mean(mean_precision))
print("mean recall:", np.mean(mean_recall), '\n')
