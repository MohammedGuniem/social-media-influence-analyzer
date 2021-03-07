import math


class TFIDF:
    def __init__(self, X):
        self.TF = self.tf(X)
        self.IDF = self.idf(X)

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

    def classify_word(self, word):
        output = {}
        for k, _ in self.TF.items():
            if word not in self.TF[k]:
                self.TF[k][word] = 0
            if word not in self.IDF:
                self.IDF[word] = 0
            output[k] = self.TF[k][word] * self.IDF[word]
        return output

    def classify_doc(self, doc):
        output = {}
        max_output = 0
        max_class = "other"
        for word in doc.split(" "):
            word_class = self.classify_word(word)
            for k, v in word_class.items():
                if k in output:
                    output[k] += v
                else:
                    output[k] = v
                if output[k] > max_output:
                    max_output = output[k]
                    max_class = k
        return max_class, max_output

    def classify(self, docs):
        classified = []
        for doc in docs:
            max_class, max_output = self.classify_doc(doc)
            classified.append(max_class)

        return classified
