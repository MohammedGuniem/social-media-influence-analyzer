from sklearn.model_selection import train_test_split
from sklearn.neural_network import MLPClassifier
import numpy as np

"""
obama: 1,
usa: 2,
election: 3,
ronaldo: 4,
soccer: 5,
winner: 6,
funny: 7,
hilarious: 8
cool: 9
politics: 10,
football: 11,
comedy: 12
"""
X = np.array([
    [1, 2, 3],
    [2, 1, 3],
    [4, 5, 6],
    [5, 6, 4],
    [7, 8, 9],
    [8, 9, 7]
])

y = np.array([10, 10, 11, 11, 12, 12])

X_train, X_test, y_train, y_test = train_test_split(X, y, random_state=1)
mlp = MLPClassifier(max_iter=1000)

mlp.fit(X_train, y_train)
print(F"accuracy: {mlp.score(X_test, y_test)}")

predictions = mlp.predict(X_test)
print(F"expected: {y_test[0]}")
print(F"got: {predictions[0]}")
