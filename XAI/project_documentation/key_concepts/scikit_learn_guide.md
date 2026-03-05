
# Scikit-learn Guide for Classification

Scikit-learn is the most popular library for machine learning in Python. It provides simple and efficient tools for data mining and data analysis.

## 1. The Scikit-learn API

Scikit-learn's API is remarkably consistent across all its algorithms. The main steps are:
1.  **Choose a model** and import its class.
2.  **Instantiate the model** with desired hyperparameters.
3.  **Arrange data** into a features matrix (X) and a target vector (y).
4.  **Fit the model** to your data by calling the `fit()` method.
5.  **Apply the model** to new data by calling `predict()` or `transform()`.

## 2. `train_test_split`

This is one of the most important functions. It splits your data into a training set (for model training) and a testing set (for model evaluation). This prevents your model from "cheating" by seeing the test data during training.

```python
from sklearn.model_selection import train_test_split

# X are your features, y is your target
X_train, X_test, y_train, y_test = train_test_split(
    X, y,
    test_size=0.3,    # 30% of data for testing
    random_state=42,  # for reproducibility
    stratify=y        # Ensures the same class proportion in train and test sets
)
```
**Note:** The `stratify=y` parameter is very important for imbalanced datasets.

## 3. Common Classifiers

### Logistic Regression
A simple but powerful linear model for classification. It's a great choice for a baseline model.

```python
from sklearn.linear_model import LogisticRegression

# 1. Instantiate the model
log_reg = LogisticRegression()

# 2. Fit the model
log_reg.fit(X_train, y_train)

# 3. Make predictions
predictions = log_reg.predict(X_test)
```

### Decision Tree
A non-linear model that learns simple decision rules inferred from the data features.

```python
from sklearn.tree import DecisionTreeClassifier

tree = DecisionTreeClassifier(max_depth=5)
tree.fit(X_train, y_train)
```

### Random Forest
An ensemble model that fits a number of decision tree classifiers on various sub-samples of the dataset and uses averaging to improve the predictive accuracy and control over-fitting.

```python
from sklearn.ensemble import RandomForestClassifier

rf = RandomForestClassifier(n_estimators=100, random_state=42)
rf.fit(X_train, y_train)
```

## 4. Evaluation Metrics

Scikit-learn provides tools to evaluate your model's performance.

```python
from sklearn.metrics import classification_report, confusion_matrix, balanced_accuracy_score

# Get predictions from your trained model
predictions = model.predict(X_test)

# Print a full report
print(classification_report(y_test, predictions))

# Print the confusion matrix
print(confusion_matrix(y_test, predictions))

# Calculate balanced accuracy
bal_acc = balanced_accuracy_score(y_test, predictions)
print(f"Balanced Accuracy: {bal_acc}")
```

The `classification_report` is extremely useful as it includes precision, recall, and F1-score for each class.
