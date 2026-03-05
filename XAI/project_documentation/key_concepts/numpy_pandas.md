
# NumPy and Pandas Guide

NumPy and Pandas are the backbone of data science in Python.

## 1. NumPy: Numerical Python

NumPy provides a powerful N-dimensional array object, which is much more efficient than Python lists for numerical operations.

### Creating NumPy Arrays

```python
import numpy as np

# Create a 1D array from a list
a = np.array([1, 2, 3, 4, 5])

# Create a 2D array (matrix)
b = np.array([[1, 2, 3], [4, 5, 6]])
```

### Array Operations

NumPy allows you to perform element-wise operations.

```python
# Add 10 to every element
c = a + 10  # array([11, 12, 13, 14, 15])

# Multiply every element by 2
d = a * 2   # array([2, 4, 6, 8, 10])
```

### Why NumPy?
For machine learning, your dataset is typically represented as a NumPy array. Features are in a 2D array (X) and the target is in a 1D array (y).

---

## 2. Pandas: Data Analysis Library

Pandas provides high-performance, easy-to-use data structures and data analysis tools. The primary data structure is the **DataFrame**.

### What is a DataFrame?
A DataFrame is a 2D labeled data structure with columns of potentially different types. You can think of it like a spreadsheet or a SQL table.

### Creating a DataFrame

```python
import pandas as pd

# From a dictionary
data = {'Name': ['Alice', 'Bob', 'Charlie'],
        'Age': [25, 30, 35]}
df = pd.DataFrame(data)
```

### Reading Data from a File

This is the most common way to create a DataFrame.

```python
# Read a CSV file into a DataFrame
df = pd.read_csv('path/to/your/dataset.csv')
```

### Essential DataFrame Operations

#### Viewing Data
```python
# View the first 5 rows
print(df.head())

# Get a summary of the DataFrame
print(df.info())

# Get descriptive statistics
print(df.describe())
```

#### Selecting Data
```python
# Select a single column (returns a Series)
ages = df['Age']

# Select multiple columns (returns a DataFrame)
subset = df[['Name', 'Age']]

# Select rows based on a condition
old_people = df[df['Age'] > 30]
```

#### Handling Missing Data
```python
# Check for missing values
print(df.isnull().sum())

# Drop rows with any missing values
df_cleaned = df.dropna()

# Fill missing values with the mean
df_filled = df.fillna(df.mean())
```

#### Value Counts
This is crucial for checking class imbalance.

```python
# Get the counts of each unique value in a column
class_distribution = df['target_column'].value_counts()
print(class_distribution)
```
