# -*- coding: utf-8 -*-
"""UniversityEligiblityPredictor.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1_IzZRrb5Csk7M0kiyTwbR4bStolM9rQC

IMPORTING THE LIBRARIES
"""

# Commented out IPython magic to ensure Python compatibility.
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
# %matplotlib inline

"""READING & ANALYSING THE DATASET"""

import os, types
import pandas as pd
from botocore.client import Config
import ibm_boto3

def __iter__(self): return 0

# @hidden_cell
# The following code accesses a file in your IBM Cloud Object Storage. It includes your credentials.
# You might want to remove those credentials before you share the notebook.
cos_client = ibm_boto3.client(service_name='s3',
    ibm_api_key_id='ut2IQbYkK0twq-ioJvvPu_OEsnzdL3IHAE_keFMVan8Q',
    ibm_auth_endpoint="https://iam.cloud.ibm.com/oidc/token",
    config=Config(signature_version='oauth'),
    endpoint_url='https://s3.private.us.cloud-object-storage.appdomain.cloud')

bucket = 'universityeligiblitypredictor-donotdelete-pr-hrjenb83oc8tgu'
object_key = 'Admission_Predict.csv'

body = cos_client.get_object(Bucket=bucket,Key=object_key)['Body']
# add missing __iter__ method, so pandas accepts body as file-like object
if not hasattr(body, "__iter__"): body.__iter__ = types.MethodType( __iter__, body )

data = pd.read_csv(body)
data.head()

data.drop(["Serial No."], axis=1, inplace=True)

data.head()

data.describe()

data.info()

"""HANDLING MISSING VALUES"""

data.isnull().sum()

"""DATA VISUALIZATION"""

plt.scatter(data['GRE Score'],data['CGPA'])
plt.title('CGPA vs GRE Score')
plt.xlabel('GRE Score')
plt.ylabel('CGPA')
plt.show()

plt.scatter(data['CGPA'],data['SOP'])
plt.title('SOP for CGPA')
plt.xlabel('CGPA')
plt.ylabel('SOP')
plt.show()

data[data.CGPA >= 8.5].plot(kind='scatter', x='GRE Score', y='TOEFL Score',color="BLUE")

plt.xlabel("GRE Score")
plt.ylabel("TOEFL SCORE")
plt.title("CGPA>=8.5")
plt.grid(True)

plt.show()

data["GRE Score"].plot(kind = 'hist',bins = 200,figsize = (6,6))

plt.title("GRE Scores")
plt.xlabel("GRE Score")
plt.ylabel("Frequency")

plt.show()

p = np.array([data["TOEFL Score"].min(),data["TOEFL Score"].mean(),data["TOEFL Score"].max()])
r = ["Worst","Average","Best"]
plt.bar(p,r)

plt.title("TOEFL Scores")
plt.xlabel("Level")
plt.ylabel("TOEFL Score")

plt.show()

g = np.array([data["GRE Score"].min(),data["GRE Score"].mean(),data["GRE Score"].max()])
h = ["Worst","Average","Best"]
plt.bar(g,h)

plt.title("GRE Scores")
plt.xlabel("Level")
plt.ylabel("GRE Score")

plt.show()

plt.figure(figsize=(10, 10))

sns.heatmap(data.corr(), annot=True, linewidths=0.05, fmt= '.2f',cmap="magma")

plt.show()

data.Research.value_counts()

sns.countplot(x="University Rating",data=data)

sns.barplot(x="University Rating", y="Chance of Admit ", data=data)

"""
SPLIT THE DATA INTO TRAIN AND TEST"""

X=data.drop(['Chance of Admit '],axis=1) #input data_set
y=data['Chance of Admit '] #output labels

from sklearn.model_selection import train_test_split 
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.15)

"""
MODEL BUILDING AND TRAINING"""

from sklearn.preprocessing import MinMaxScaler
scaler=MinMaxScaler()
X_train[X_train.columns] = scaler.fit_transform(X_train[X_train.columns])
X_test[X_test.columns] = scaler.transform(X_test[X_test.columns])
X_train.head()

from sklearn.ensemble import GradientBoostingRegressor
rgr = GradientBoostingRegressor()
rgr.fit(X_train,y_train)

rgr.score(X_test,y_test)

y_predict=rgr.predict(X_test)

from sklearn.metrics import mean_squared_error, r2_score,mean_absolute_error
import numpy as np
print('Mean Absolute Error:', mean_absolute_error(y_test, y_predict))  
print('Mean Squared Error:', mean_squared_error(y_test, y_predict))  
print('Root Mean Squared Error:', np.sqrt(mean_squared_error(y_test, y_predict)))

y_train = (y_train>0.5)
y_test = (y_test>0.5)

from sklearn.linear_model._logistic import LogisticRegression

lore = LogisticRegression(random_state=0, max_iter=1000)

lr = lore.fit(X_train, y_train)

y_pred = lr.predict(X_test)

from sklearn.metrics import accuracy_score, recall_score, roc_auc_score, confusion_matrix

print('Accuracy Score:', accuracy_score(y_test, y_pred))  
print('Recall Score:', recall_score(y_test, y_pred))  
print('ROC AUC Score:', roc_auc_score(y_test, y_pred))
print('Confussion Matrix:\n', confusion_matrix(y_test, y_pred))

"""
SAVING THE MODELS"""

import pickle

pickle.dump(lr, open("university.pkl", "wb")) #logistic regression model
pickle.dump(rgr, open("university_percent.pkl", "wb")) #regression model

"""
HOSTING THE MODEL ON IBM"""

import pickle

!pip install ibm_watson_machine_learning

lr = pickle.load(open("university.pkl", "rb")) #logistic regression model
gd = pickle.load(open("university_percent.pkl", "rb")) #regression model

from ibm_watson_machine_learning import APIClient

uml_credentials = {
    "url": "https://us-south.ml.cloud.ibm.com",
    "apikey": "dGIxSW08kkFMfQYJQUrNhrU9VA3OHtAczqSBGZzLxtcw"
}

client = APIClient(uml_credentials)

def guid_from_space_name(client, space_name):
    space = client.spaces.get_details()
    idr = []
    for i in space['resources']:
        idr.append(i['metadata']['id'])
    return idr

space_uid = guid_from_space_name(client, "IBMprojectmodels")
print(space_uid)

client.set.default_space(space_uid[0])

client.software_specifications.list()

software_uid = client.software_specifications.get_uid_by_name('runtime-22.1-py3.9')
print(software_uid)

software_uid = client.software_specifications.get_uid_by_name('runtime-22.1-py3.9')
print(software_uid)
meta_props={
     client.repository.ModelMetaNames.NAME: "logistic_model",
     client.repository.ModelMetaNames.SOFTWARE_SPEC_UID: software_uid,
     client.repository.ModelMetaNames.TYPE: "scikit-learn_1.0"
}

#model_details =client.repository.store_model(model=lr,meta_props={
#client.repository.ModelMetaNames.NAME: "logistic_model",
#client.repository.ModelMetaNames.SOFTWARE_SPEC_UID: software_uid,
#client.repository.ModelMetaNames.TYPE: "scikit-learn_0.23"    })

#model_id = client.repository.get_model_uid(model_details)

"""MODEL DEPLOYMENT"""

model_details = client.repository.store_model(model=lr, meta_props=meta_props, training_data=None)

