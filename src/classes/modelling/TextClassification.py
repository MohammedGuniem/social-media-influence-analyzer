from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.model_selection import GridSearchCV
from sklearn.linear_model import SGDClassifier
from sklearn.naive_bayes import MultinomialNB
from sklearn.model_selection import KFold
from sklearn.pipeline import Pipeline
from dotenv import load_dotenv
import pandas as pd
import numpy as np
import random
import os


class TextClassifier:
    def __init__(self, mongo_db_connector, network_name, submissions_type, date):
        self.data = mongo_db_connector.readFromDB(
            database_name=F"{network_name}_{submissions_type}_Training_Data",
            collection_name=date,
            query={},
            single=True
        )
        self.random_state = 99

    def prepare_model(self):
        if not self.data:
            return "data not found"
        del self.data["_id"]
        self.data = self.data["training_data"]
        random.seed(self.random_state)
        random.shuffle(self.data)

        training_df = pd.DataFrame(self.data)
        features = (training_df["title"]).to_numpy()
        labels = (training_df["label"]).to_numpy()

        tuned_paramters = self.tune_model()
        alpha = tuned_paramters['best_parameters']['clf__alpha']
        use_idf = tuned_paramters['best_parameters']['tfidf__use_idf']
        ngram_range = tuned_paramters['best_parameters']['vect__ngram_range']
        self.text_clf = Pipeline([
            ('vect', CountVectorizer(ngram_range=ngram_range)),
            ('tfidf', TfidfTransformer(use_idf=use_idf)),
            ('clf', SGDClassifier(alpha=alpha, random_state=self.random_state)),
        ])
        self.text_clf.fit(features, labels)
        return "model is fitted and ready for use"

    def tune_model(self):
        df = pd.DataFrame(self.data)
        features = (df["title"]).to_numpy()
        labels = (df["label"]).to_numpy()

        text_clf = Pipeline([
            ('vect', CountVectorizer()),
            ('tfidf', TfidfTransformer()),
            ('clf', SGDClassifier(random_state=self.random_state)),
        ])

        training_percentage = 0.8
        testing_percentage = 0.2
        X_train, X_test = list(features[:int(training_percentage*len(features))]
                               ), list(features[:int(testing_percentage*len(features))])
        y_train, y_test = list(labels[:int(training_percentage*len(features))]
                               ), list(labels[:int(testing_percentage*len(features))])

        parameters = {
            'vect__ngram_range': [(1, 1), (1, 2)],
            'tfidf__use_idf': (True, False),
            'clf__alpha': (1e-2, 1e-3),
        }
        gs_clf = GridSearchCV(text_clf, parameters, cv=8, n_jobs=-1)

        gs_clf.fit(X_train, y_train)

        y_pred = gs_clf.predict(X_test)

        tunning_results = {
            "best_score": gs_clf.best_score_,
            "best_parameters": gs_clf.best_params_
        }
        return tunning_results

    def evaluate_model(self):
        df = pd.DataFrame(self.data)
        features = (df["title"]).to_numpy()
        labels = (df["label"]).to_numpy()
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
        kf = KFold(n_splits=5, shuffle=True, random_state=self.random_state)
        for train_index, test_index in kf.split(features):
            X_train, X_test = list(features[train_index]), list(
                features[test_index])
            y_train, y_test = list(
                labels[train_index]), list(labels[test_index])
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

        evaluation_result = {
            "accuracy": np.mean(accuracy_scores),
            "precision": np.mean(precision_scores),
            "recall": np.mean(recall_scores),
            "F1_score": np.mean(f1_scores)
        }
        return evaluation_result

    def get_report(self):
        df = pd.DataFrame(self.data)
        features = (df["title"]).to_numpy()
        labels = (df["label"]).to_numpy()
        text_clf = Pipeline([
            ('vect', CountVectorizer(ngram_range=(1, 2))),
            ('tfidf', TfidfTransformer(use_idf=True)),
            ('clf', SGDClassifier(alpha=0.001, random_state=self.random_state)),
        ])
        training_percentage = 0.8
        testing_percentage = 0.2
        X_train, X_test = list(features[:int(training_percentage*len(features))]
                               ), list(features[-int(testing_percentage*len(features)):])
        y_train, y_test = list(labels[:int(training_percentage*len(features))]
                               ), list(labels[-int(testing_percentage*len(features)):])

        text_clf.fit(X_train, y_train)
        y_pred = text_clf.predict(X_test)
        labels = list(set(labels))
        class_report = classification_report(
            y_test, y_pred, target_names=labels, output_dict=True, labels=labels)
        conf_matrix = confusion_matrix(y_test, y_pred, labels=labels)

        return class_report, conf_matrix, labels

    def classify_title(self, title):
        return self.text_clf.predict([title])[0]
