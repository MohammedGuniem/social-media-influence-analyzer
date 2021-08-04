import pandas as pd

data = [
    {
        "title": "title - 1",
        "label": "label - 1"
    },
    {
        "title": "title - 2",
        "label": "label - 2"
    },
    {
        "title": "title - 3",
        "label": "label - 3"
    },
    {
        "title": "title - 4",
        "label": "label - 4"
    },
    {
        "title": "title - 5",
        "label": "label - 5"
    },
    {
        "title": "title - 6",
        "label": "label - 6"
    },
    {
        "title": "title - 7",
        "label": "label - 7"
    },
    {
        "title": "title - 8",
        "label": "label - 8"
    },
    {
        "title": "title - 9",
        "label": "label - 9"
    },
    {
        "title": "title - 10",
        "label": "label - 10"
    },
]

print("----------------------init_eval_data-----------------------")
init_eval_data = data[0:int(0.80*len(data))]
df = pd.DataFrame(init_eval_data)
features = (df["title"]).to_numpy()
labels = (df["label"]).to_numpy()
print(features)
print(labels)
print("-----------------------------------------------------------")

print("----------------------tuning-----------------------")
tuning_data = data[0:int(0.80*len(data))]
df = pd.DataFrame(tuning_data)
features = (df["title"]).to_numpy()
labels = (df["label"]).to_numpy()
print(features)
print(labels)
print("-----------------------------------------------------------")

print("----------------------final evaluation-----------------------")
df = pd.DataFrame(data)
features = (df["title"]).to_numpy()
labels = (df["label"]).to_numpy()
training_percentage = 0.8
testing_percentage = 0.2
X_train, X_test = list(features[:int(training_percentage*len(features))]
                       ), list(features[-int(testing_percentage*len(features)):])
y_train, y_test = list(labels[:int(training_percentage*len(features))]
                       ), list(labels[-int(testing_percentage*len(features)):])
print(X_train)
print(y_train)
print(X_test)
print(y_test)
print("-----------------------------------------------------------")
