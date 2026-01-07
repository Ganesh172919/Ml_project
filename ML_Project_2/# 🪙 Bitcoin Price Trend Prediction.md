# 🪙 Bitcoin Price Trend Prediction

This project predicts **Bitcoin's price movement** (up or down) using **Machine Learning** models such as **Logistic Regression**, **Support Vector Classifier (SVC)**, and **XGBoost**.  
It includes data visualization, preprocessing, feature engineering, and model evaluation steps.

---

## 📘 Project Overview

This project performs the following steps:

1. **Data Loading** — Reads historical Bitcoin data from `bitcoin.csv`.  
2. **Exploratory Data Analysis (EDA)** — Analyzes key columns such as `Open`, `High`, `Low`, and `Close` prices using graphs and statistics.  
3. **Feature Engineering** — Creates new features to improve prediction:
   - `open-close` → Difference between open and close prices  
   - `high-low` → Difference between high and low prices  
   - `is_quarter_end` → Identifies quarter-end months (March, June, September, December)  
4. **Model Training** — Trains multiple ML models:
   - Logistic Regression  
   - Support Vector Classifier (SVC with polynomial kernel)  
   - XGBoost Classifier  
5. **Model Evaluation** — Calculates AUC (Area Under Curve) scores for both training and validation data.  
6. **Visualization** — Displays correlation heatmaps, data distributions, and confusion matrices.

---

## 🧠 Machine Learning Models Used

| Model | Description | Purpose |
|--------|--------------|----------|
| **Logistic Regression** | A linear model used for binary classification | Baseline prediction model |
| **SVC (Polynomial Kernel)** | A non-linear classifier | Captures complex patterns in Bitcoin price data |
| **XGBoost** | A gradient boosting model | Provides high accuracy and handles non-linearity |

---

## 📊 Data Visualization

The project includes multiple plots to better understand data patterns:
- Bitcoin **closing price trends** over time  
- **Distribution plots** and **box plots** for features  
- **Correlation heatmap**  
- **Pie chart** of target variable distribution  
- **Confusion matrix** for classification results  

---

## 🧩 Dependencies

Install the following Python libraries before running the script:

```bash
pip install numpy pandas matplotlib seaborn scikit-learn xgboost
