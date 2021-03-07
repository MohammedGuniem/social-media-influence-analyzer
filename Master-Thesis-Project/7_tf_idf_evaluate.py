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

features = []
labels = []
for category, titles in docs.items():
    for title in titles:
        features.append(title)
        labels.append(category)

number_of_docs = []
number_of_docs_f1 = []
number_of_docs_accuracy = []
number_of_docs_precesion = []
number_of_docs_recall = []

features = np.array(features)
labels = np.array(labels)

for doc_num in range(52, len(features), 50):
    X = features[0:doc_num]
    y = labels[0:doc_num]
    #print(F"Using {len(X)} docs dataset")

    accuracy_arr = []
    precision_arr = []
    recall_arr = []
    f_score_arr = []
    kf = KFold(n_splits=5, shuffle=True, random_state=10)
    for train_index, test_index in kf.split(X):
        X_train, X_test = list(X[train_index]), list(X[test_index])
        y_train, y_test = list(y[train_index]), list(y[test_index])

        training_data = {}
        for index in range(0, len(y_train), 1):
            category = y_train[index]
            if category in training_data:
                training_data[category].append(X_train[index])
            else:
                training_data[category] = [X_train[index]]
        tf_idf = TFIDF(training_data)

        y_classified = tf_idf.classify(X_test)
        accuracy_arr.append(accuracy_score(y_test, y_classified))
        precision_arr.append(precision_score(y_test, y_classified, zero_division=0,
                                             average='weighted', labels=np.unique(y_test)))
        recall_arr.append(recall_score(y_test, y_classified, zero_division=0,
                                       average='weighted', labels=np.unique(y_test)))
        f_score_arr.append(f1_score(y_test, y_classified, zero_division=0,
                                    average='weighted', labels=np.unique(y_test)))

    accuracy = np.mean(accuracy_arr)
    precision = np.mean(precision_arr)
    recall = np.mean(recall_arr)
    f1 = np.mean(f_score_arr)

    """
    print(F"accuracy: {accuracy}")
    print(F"precision: {precision}")
    print(F"recall: {recall}")
    print(F"F1-score: {f1}")
    print()
    """
    number_of_docs.append(len(X))
    number_of_docs_f1.append(f1)
    number_of_docs_accuracy.append(accuracy)
    number_of_docs_precesion.append(precision)
    number_of_docs_recall.append(recall)

highest_accuracy = max(number_of_docs_accuracy)
opt_doc_num_accuracy = number_of_docs[number_of_docs_accuracy.index(
    highest_accuracy)]

highest_precesion = max(number_of_docs_precesion)
opt_doc_num_precesion = number_of_docs[number_of_docs_precesion.index(
    highest_precesion)]

highest_recall = max(number_of_docs_recall)
opt_doc_num_recall = number_of_docs[number_of_docs_recall.index(
    highest_recall)]

highest_f1 = max(number_of_docs_f1)
opt_doc_num_f1 = number_of_docs[number_of_docs_f1.index(
    highest_f1)]

print(
    F"optimal accuracy: {highest_accuracy} at {opt_doc_num_accuracy} documents.")
print(
    F"optimal precision: {highest_precesion} at {opt_doc_num_precesion} documents.")
print(
    F"optimal recall: {highest_recall} at {opt_doc_num_recall} documents.")
print(
    F"optimal F1-score: {highest_f1} at {opt_doc_num_f1} documents.")

statistics_methods.multi_line_plot(
    x=number_of_docs,
    Y=[number_of_docs_f1, number_of_docs_accuracy,
        number_of_docs_precesion, number_of_docs_recall],
    optimal_x=[opt_doc_num_f1, opt_doc_num_f1],
    optimal_y=[0, 1],
    optimal_label=F"optimal solution at ({opt_doc_num_f1}) documents",
    plot_labels=["F1-score", "accuracy", "precesion", "recall"],
    xlabel="number of documents",
)

"""
optimal accuracy: 0.7747540983606557 at 302 documents.
optimal precision: 0.9852760120441619 at 302 documents.
optimal recall: 0.7747540983606557 at 302 documents.   
optimal F1-score: 0.8669082595668056 at 302 documents. 
"""
