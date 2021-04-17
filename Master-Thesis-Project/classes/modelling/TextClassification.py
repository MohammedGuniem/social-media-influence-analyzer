from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.linear_model import SGDClassifier
from sklearn.pipeline import Pipeline
import pandas as pd


class TextClassifier:
    def __init__(self, mongo_db_connector, network_name, submissions_type, date):
        data = mongo_db_connector.readFromDB(
            database_name=F"{network_name}_{submissions_type}_Training_Data",
            collection_name=date,
            query={},
            single=True
        )
        del data["_id"]

        data = pd.DataFrame(data["training_data"])
        features = (data["title"]).to_numpy()
        labels = (data["label"]).to_numpy()

        self.text_clf = Pipeline([
            ('vect', CountVectorizer(ngram_range=(1, 2))),
            ('tfidf', TfidfTransformer(use_idf=True)),
            ('clf', SGDClassifier(alpha=0.001, random_state=99)),
        ])
        self.text_clf.fit(features, labels)

    def classify_title(self, title):
        return self.text_clf.predict([title])[0]
