import math
from classes.tf_idf.TFIDF import TFIDF

train_X = {
    "comedy": ["This is a sample", "a"],
    "politics": ["This is another example", "example", "example", "another"]
}
tf_idf = TFIDF()

tf_idf.build(train_X)

res = tf_idf.predict("example")
for k, v, in res.items():
    print(F"{k}: {v}")
print("Done")
