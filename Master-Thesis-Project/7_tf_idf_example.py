import math
from classes.tf_idf.TFIDF import TFIDF

train_X = {
    "comedy": ["This is as sample"],
    "politics": ["This is another another example example example"],
    "sports": ["what a match"]
}
tf_idf = TFIDF()

tf_idf.build(train_X)

res = tf_idf.classify_word("example")
for k, v, in res.items():
    print(F"{k}: {v}")

print()
res = tf_idf.classify_word("as")
for k, v, in res.items():
    print(F"{k}: {v}")
print()

res = tf_idf.classify_word("This")
for k, v, in res.items():
    print(F"{k}: {v}")
print()

max_class, max_output = tf_idf.classify_doc("This example as")
print(F"{max_class}: {max_output}")
