
import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder
"""
# creating initial dataframe
bridge_types = ('Arch', 'Beam', 'Truss', 'Cantilever',
                'Tied Arch', 'Suspension', 'Cable')
bridge_df = pd.DataFrame(bridge_types, columns=['Bridge_Types'])
# creating instance of labelencoder
labelencoder = LabelEncoder()
labelencoder.fit(bridge_df['Bridge_Types'])
# Assigning numerical values and storing in another column
bridge_df['Bridge_Types_Cat'] = labelencoder.transform(
    bridge_df['Bridge_Types'])
print(bridge_df)

# creating initial dataframe
bridge_types = ('Suspension', 'Cable')
bridge_df = pd.DataFrame(bridge_types, columns=['Bridge_Types'])
# creating instance of labelencoder
#labelencoder = LabelEncoder()
# Assigning numerical values and storing in another column
bridge_df['Bridge_Types_Cat'] = labelencoder.transform(
    bridge_df['Bridge_Types'])
print(bridge_df)
"""
label_enc = LabelEncoder()
y = ['comedy', 'politics', 'comedy', 'sport']
label_enc.fit(y)

encoded_labels = label_enc.transform(y)
print(encoded_labels)
decoded_labels = label_enc.inverse_transform(encoded_labels)
print(decoded_labels)


encoded = label_enc.transform(['sport', 'politics', 'politics'])
print(encoded)
decoded_labels = label_enc.inverse_transform(encoded)
print(decoded_labels)

"""
from sklearn.preprocessing import OneHotEncoder
enc = OneHotEncoder(handle_unknown='ignore')
X = [['Male'], ['Female'], ['Female'], ['test']]
enc.fit(X)

encoded = enc.transform([['Female'], ['Female'], ['Male']]).toarray()
print(encoded)
decoded = enc.inverse_transform(encoded)
print(decoded)


encoded = enc.transform([['Female'], ['go'], ['Male']]).toarray()
print(encoded)
"""
