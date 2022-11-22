import time

import numpy as np
import sklearn
from sktime.classification.interval_based import TimeSeriesForestClassifier
from sktime.datasets import load_arrow_head
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from sktime.transformations.panel.rocket import Rocket
from sklearn.linear_model import RidgeClassifierCV

X, y = load_arrow_head()
X_train, X_test, y_train, y_test = train_test_split(X, y)
start = time.time()
classifier = TimeSeriesForestClassifier()
classifier.fit(X_train, y_train)
y_pred = classifier.predict(X_test)
end = time.time()
print("v1 tempo:::", end-start)
ac_s = accuracy_score(y_test, y_pred)


print(ac_s)


###using ROCKET

# X_train, y_train = load_arrow_head(split="train", return_X_y=True)
start = time.time()
rocket = Rocket()  # by default, ROCKET uses 10,000 kernels
rocket.fit(X_train)
X_train_transform = rocket.transform(X_train)

classifier = RidgeClassifierCV(alphas=np.logspace(-3, 3, 10), normalize=True)
classifier.fit(X_train_transform, y_train)
##test loading
# X_test, y_test = load_arrow_head(split="test", return_X_y=True)
X_test_transform = rocket.transform(X_test)
y_pred = classifier.predict(X_test_transform)

end=time.time()
print("v2 tempo:::", end-start)


# print(sklearn.metrics.accuracy_score(y_test, y_pred))
print(classifier.score(X_test_transform, y_test))





