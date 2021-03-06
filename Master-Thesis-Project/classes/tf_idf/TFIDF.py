import math


class TFIDF:
    def __init__(self):
        self.TF = {}
        self.IDF = {}

    def tf(self, X):
        TFs = {}
        for category, docs in X.items():
            TFs[category] = {}
            category_doc = (" ".join(docs)).split(" ")
            for word in category_doc:
                TFs[category][word] = category_doc.count(
                    word) / len(category_doc)
        return TFs

    def idf(self, X):
        IDFs = {}

        docs_count = len(X.keys())

        all_words = []
        temp = {}
        for k, v in X.items():
            doc_text = " ".join(list(v))
            doc_words = doc_text.split(" ")
            temp[k] = doc_words
            all_words += doc_words

        for word in all_words:
            occurence_count = 0
            for k, doc_words in temp.items():
                if word in doc_words:
                    occurence_count += 1
            IDFs[word] = abs(math.log(occurence_count/docs_count, 10))
            # IDFs[word] = occurence_count/docs_count

        return IDFs

    def build(self, X):
        self.TF = self.tf(X)
        self.IDF = self.idf(X)

    def predict(self, x):
        temp = {}
        for word in x.split(" "):
            for k, _ in self.TF.items():
                if word not in self.TF[k]:
                    self.TF[k][word] = 0
                if word not in self.IDF:
                    self.IDF[word] = 0
                temp[k] = self.TF[k][word] * self.IDF[word]
        return temp
