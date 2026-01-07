# 💳 Credit Card Fraud Detection

A machine learning project to detect fraudulent credit card transactions using a **Random Forest Classifier**.  
This project performs data preprocessing, visualization, model training, and evaluation to identify potential frauds from transaction data.

---

## 📘 Table of Contents
- [Overview](#overview)
- [Dataset](#dataset)
- [Requirements](#requirements)
- [Installation](#installation)
- [Usage](#usage)
- [Model Evaluation](#model-evaluation)
- [Results](#results)
- [Visualization](#visualization)
- [License](#license)

---

## 🧩 Overview
Credit card fraud is a major problem in the financial sector.  
This project classifies transactions as **legitimate (0)** or **fraudulent (1)** using **Random Forest**, a supervised learning algorithm.  
Because fraud cases are rare, the dataset is **highly imbalanced**, making it important to focus on **precision**, **recall**, and **F1-score**.

---

## 📊 Dataset
Dataset used: [Credit Card Fraud Detection Dataset](https://www.kaggle.com/mlg-ulb/creditcardfraud)

**Features:**
- `Time`: Seconds elapsed between this transaction and the first transaction.
- `V1–V28`: Principal components obtained using PCA.
- `Amount`: Transaction amount.
- `Class`: Response variable (1 for fraud, 0 for valid).

---

## 🧠 Requirements
Install the dependencies before running the script.

```bash
pip install numpy pandas matplotlib seaborn scikit-learn
