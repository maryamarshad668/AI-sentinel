# task 1

import pandas as pd
from sklearn.impute import SimpleImputer
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

data = pd.read_csv("ensemble_data.csv")

x = data.iloc[:, :-1]   
y = data.iloc[:, -1]    

imputer = SimpleImputer(strategy='mean')
x = imputer.fit_transform(x)

xtrain, xtest, ytrain, ytest = train_test_split( x, y, test_size=0.2, random_state=42)
scaler = StandardScaler()
xtrain = scaler.fit_transform(xtrain)  
xtest = scaler.transform(xtest)        

print("training data:", xtrain.shape)
print("testing data:", xtest.shape)

# task 2

from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import accuracy_score

knn = KNeighborsClassifier(n_neighbors=5)
knn.fit(xtrain, ytrain)
ypredict = knn.predict(xtest)
accuracy = accuracy_score(ytest, ypredict)

print("knn accuracy:", accuracy)

# task 3

from sklearn.tree import DecisionTreeClassifier
from sklearn.tree import plot_tree
import matplotlib.pyplot as plt

depth5 = DecisionTreeClassifier(criterion='gini', max_depth=5)
depth5.fit(xtrain, ytrain)

predictdepth5 = depth5.predict(xtest)
accuracydepth5 = accuracy_score(ytest, predictdepth5)

print("decision tree d=5 accuracy:", accuracydepth5)

fulltree = DecisionTreeClassifier(criterion='gini', max_depth=None)
fulltree.fit(xtrain, ytrain)
predictfull = fulltree.predict(xtest)
accuracyfull = accuracy_score(ytest, predictfull)

print("decision tree fyll d accuracy:", accuracyfull)

# task 4

kvalues = [1,3,5,7,9,11,15]
accuracy = []
for k in kvalues:
 
    model = KNeighborsClassifier(n_neighbors=k)
    model.fit(xtrain, ytrain)
    
    pred = model.predict(xtest)
    acc = accuracy_score(ytest, pred)
    accuracy.append(acc)

plt.plot(kvalues, accuracy, marker='o')
plt.xlabel("k value")
plt.ylabel("test accuracy")
plt.title("kNN accuracy for different K values")
plt.show()

# task 5

import time
print("model----train---- acc Test---- accTime")

start = time.time()
knn = KNeighborsClassifier(n_neighbors=5)
knn.fit(xtrain, ytrain)

train_knn = accuracy_score(ytrain, knn.predict(xtrain))
test_knn = accuracy_score(ytest, knn.predict(xtest))
end = time.time()

print("KNN k=5 ----", round(train_knn,3), "----", round(test_knn,3), "----", round(end-start,4))

start = time.time()

tree5 = DecisionTreeClassifier(max_depth=5)
tree5.fit(xtrain, ytrain)
train_tree5 = accuracy_score(ytrain, tree5.predict(xtrain))
test_tree5 = accuracy_score(ytest, tree5.predict(xtest))

end = time.time()

print("Tree d=5----", round(train_tree5,3), "----", round(test_tree5,3), "----", round(end-start,4))

start = time.time()

tree_full = DecisionTreeClassifier(max_depth=None)
tree_full.fit(xtrain, ytrain)
train_full = accuracy_score(ytrain, tree_full.predict(xtrain))
test_full = accuracy_score(ytest, tree_full.predict(xtest))

end = time.time()

print("full tree ----", round(train_full,3), "----", round(test_full,3), "----", round(end-start,4))