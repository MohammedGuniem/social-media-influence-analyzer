import sys
for path in sys.path:
    if "Influence_area_detection_model" in path:
        main_project_path = "\\".join(path.split("\\")[0:-1])
        sys.path.append(main_project_path)
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from classes.database_connectors.MongoDBConnector import MongoDBConnector
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
import sys
import os

load_dotenv()

# Database connector
mongo_db_host = os.environ.get('mongo_db_host')
mongo_db_port = os.environ.get('mongo_db_port')
mongo_db_user = os.environ.get('mongo_db_user')
mongo_db_pass = os.environ.get('mongo_db_pass')
mongo_db_connector = MongoDBConnector(
    host=mongo_db_host, port=int(mongo_db_port), user=mongo_db_user, passowrd=mongo_db_pass)

data = mongo_db_connector.readFromDB(database_name="Reddit_Rising_Training_Data", query={
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
    ('clf', SGDClassifier(random_state=99)),
])

"""
('clf', MultinomialNB()),
('clf', SGDClassifier(loss='hinge', penalty='l2',
    alpha=1e-3, random_state=42,
        max_iter=5, tol=None)),
"""

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

print(F"best score: {gs_clf.best_score_}")
print()
for param_name in sorted(parameters.keys()):
    print("%s: %r" % (param_name, gs_clf.best_params_[param_name]))
