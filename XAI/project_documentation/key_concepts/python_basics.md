
# Python Basics for Machine Learning

This guide covers the fundamental Python concepts you need for this project.

## 1. Variables and Data Types

In Python, you can create a variable by assigning a value to it.

```python
# A number (integer)
project_day = 1

# A string (text)
project_name = "XAI Project"

# A floating-point number
accuracy = 95.5

# A boolean (True/False)
is_imbalanced = True
```

## 2. Data Structures

### Lists
A list is a collection of items in a particular order.

```python
# A list of evaluation metrics
metrics = ["accuracy", "recall", "f1-score"]

# Accessing items
first_metric = metrics[0]  # "accuracy"

# Adding an item
metrics.append("precision")
```

### Dictionaries
A dictionary stores data in key-value pairs.

```python
# A dictionary to store model performance
model_performance = {
    "model_name": "Logistic Regression",
    "f1_score": 0.65,
    "recall": 0.58
}

# Accessing a value by its key
f1 = model_performance["f1_score"] # 0.65
```

## 3. Control Flow

### `if-elif-else` Statements
Used to run code based on conditions.

```python
if recall < 0.6:
    print("Model performance is poor on the minority class.")
elif recall < 0.8:
    print("Model performance is acceptable, but can be improved.")
else:
    print("Model performance is good.")
```

### `for` Loops
Used to iterate over a sequence (like a list).

```python
# Print each metric
for metric in metrics:
    print(f"Evaluating with: {metric}")
```

## 4. Functions

Functions are reusable blocks of code. They help organize your program.

```python
# A function to calculate balanced accuracy
def calculate_balanced_accuracy(tp, tn, total_pos, total_neg):
    """Calculates the balanced accuracy."""
    recall_pos = tp / total_pos
    recall_neg = tn / total_neg
    return (recall_pos + recall_neg) / 2

# Using the function
balanced_acc = calculate_balanced_accuracy(tp=50, tn=900, total_pos=100, total_neg=1000)
print(f"Balanced Accuracy: {balanced_acc}")
```

## 5. Comments

Use the `#` symbol to add comments to your code. Comments are ignored by Python but are essential for explaining what your code does.

```python
# This line loads the dataset from a CSV file
df = pd.read_csv("my_data.csv")
```

## 6. Importing Libraries

To use external libraries like Pandas or Scikit-learn, you need to import them first.

```python
# Import the entire library
import pandas

# Import the library and give it an alias
import pandas as pd

# Import a specific function or class from a library
from sklearn.model_selection import train_test_split
```
This is a foundational skill for any data science project.
