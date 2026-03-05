# Learning & Code Guide: Handling Class Imbalance with Oversampling and XAI

This is your deep dive into the full project: theory, concepts, pitfalls, and reusable code. It complements the notebook `Handling_Class_Imbalance_XAI.ipynb` and gives you an end‑to‑end understanding in one place.

## Table of Contents
- 1. Problem Framing & Goals
- 2. Data & Preprocessing Foundations
- 3. Metrics Under Imbalance (Math + Intuition)
- 4. Baselines, Pipelines, and Proper Splits
- 5. Oversampling: SMOTE Family, ADASYN, Trade‑offs
- 6. Correct Experimental Protocol (No Leakage!)
- 7. Thresholds, Calibration, and Costs
- 8. Model Explainability with SHAP (Global + Local)
- 9. Evaluating Synthetic Data Quality
- 10. Cross‑Validation and Hyperparameter Tuning
- 11. Robustness, Fairness, and Ethics
- 12. Reproducibility & Performance Tips
- 13. Minimal End‑to‑End Script
- 14. Practical Checklist
- 15. References & Further Reading
- 16. Glossary

---

## 1) Problem Framing & Goals
Imbalanced classification occurs when the positive class is rare. In the stroke dataset, only a small fraction of patients have a stroke (label 1). A naive “always 0” model can achieve high accuracy but fails at the actual objective: catching positives.

Goal: Improve minority recall and F1 without inflating false positives beyond acceptable costs, and validate with explainability to ensure the model learns medically plausible patterns.

High‑level workflow:
```
Data → Split → Preprocess → Baseline → Oversample (train only) →
Train models → Evaluate (ROC/PR, minority recall/F1) → XAI with SHAP →
Sanity checks on synthetic data → Threshold/Calibration → Report
```

Dataset placement: put `healthcare-dataset-stroke-data.csv` at the repo root (alongside the notebook).

---

## 2) Data & Preprocessing Foundations

- Pandas DataFrame is your workhorse for tabular data.
- Key EDA: `df.head()`, `df.info()`, `df.describe()`, `df.isnull().sum()`.
- Handle rare categories (e.g., `gender == 'Other'` with frequency 1) carefully; collapsing to mode is pragmatic.
- Missing values: impute numerics (mean/median) and categoricals (most frequent). Scale numerics; one‑hot encode categoricals.

Code skeleton:
```python
import numpy as np, pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.impute import SimpleImputer
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline

df = pd.read_csv('healthcare-dataset-stroke-data.csv')
df = df.drop(columns=['id'])
df['gender'] = df['gender'].replace('Other', df['gender'].mode()[0])

X, y = df.drop('stroke', axis=1), df['stroke']
cat = X.select_dtypes(include=['object']).columns
num = X.select_dtypes(include=np.number).columns

num_tf = Pipeline([
    ('imputer', SimpleImputer(strategy='mean')),
    ('scaler', StandardScaler())
])
cat_tf = Pipeline([
    ('imputer', SimpleImputer(strategy='most_frequent')),
    ('onehot', OneHotEncoder(handle_unknown='ignore'))
])

preprocessor = ColumnTransformer([
    ('num', num_tf, num),
    ('cat', cat_tf, cat)
])

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)
```

---

## 3) Metrics Under Imbalance (Math + Intuition)

Confusion matrix for binary classification:

- True Positives (TP): predict 1, actual 1
- False Positives (FP): predict 1, actual 0
- True Negatives (TN): predict 0, actual 0
- False Negatives (FN): predict 0, actual 1

Key metrics:

- Precision: $\text{P} = \frac{\mathrm{TP}}{\mathrm{TP}+\mathrm{FP}}$
- Recall (Sensitivity): $\text{R} = \frac{\mathrm{TP}}{\mathrm{TP}+\mathrm{FN}}$
- F1: $\text{F1} = 2\cdot \frac{\text{P}\cdot\text{R}}{\text{P}+\text{R}}$
- $F_\beta$: $F_\beta = (1+\beta^2) \cdot \frac{\text{P}\cdot\text{R}}{\beta^2\cdot\text{P}+\text{R}}$ (use $\beta>1$ to favor recall)
- ROC‑AUC: threshold‑free discrimination measure; can be optimistic under heavy imbalance.
- PR‑AUC (Average Precision): more informative when positives are rare.

Remember: high accuracy can hide a very low recall for the minority class.

---

## 4) Baselines, Pipelines, and Proper Splits

Start with simple, strong baselines and consistent preprocessing:
```python
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier

log_reg = Pipeline([
    ('pre', preprocessor),
    ('clf', LogisticRegression(max_iter=1000, class_weight='balanced', random_state=42))
])
rf = Pipeline([
    ('pre', preprocessor),
    ('clf', RandomForestClassifier(class_weight='balanced', random_state=42))
])

log_reg.fit(X_train, y_train)
rf.fit(X_train, y_train)
```

Why `class_weight='balanced'`? It scales loss contributions inversely to class frequency—a quick baseline before oversampling.

---

## 5) Oversampling: SMOTE Family, ADASYN, Trade‑offs

Oversampling increases minority presence in the training data:

- Random Oversampling: duplicates minority rows; can overfit.
- SMOTE: interpolates between minority neighbors to synthesize new samples.
- Borderline‑SMOTE: focuses on minority samples near decision boundaries.
- ADASYN: emphasizes hard‑to‑learn regions (more majority neighbors).
- Variants (for awareness): SVM‑SMOTE, KMeansSMOTE.

Considerations:
- k‑neighbors (default 5) affects diversity and potential noise.
- Oversampling high‑dimensional sparse one‑hot spaces may create unusual combinations; track feature realism post‑encoding.

Basic usage:
```python
from imblearn.over_sampling import SMOTE
smote = SMOTE(random_state=42)
X_train_pp = preprocessor.fit_transform(X_train)
X_test_pp  = preprocessor.transform(X_test)
X_train_smote, y_train_smote = smote.fit_resample(X_train_pp, y_train)
```

---

## 6) Correct Experimental Protocol (No Leakage!)

Golden rule: never oversample before the split, and never use test data in oversampling. Prefer to embed oversampling inside a pipeline used within each cross‑validation fold:

```python
from imblearn.pipeline import Pipeline as ImbPipeline
from imblearn.over_sampling import SMOTE
from sklearn.model_selection import StratifiedKFold, GridSearchCV
from sklearn.ensemble import RandomForestClassifier

imb_pipe = ImbPipeline(steps=[
    ('pre', preprocessor),
    ('smote', SMOTE(random_state=42)),
    ('clf', RandomForestClassifier(random_state=42))
])

param_grid = {
    'smote__k_neighbors': [3, 5, 7],
    'clf__n_estimators': [200, 400],
    'clf__max_depth': [None, 10, 20]
}

cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
gscv = GridSearchCV(
    estimator=imb_pipe,
    param_grid=param_grid,
    scoring='average_precision',  # PR‑AUC
    n_jobs=-1,
    cv=cv
)
gscv.fit(X_train, y_train)
best_model = gscv.best_estimator_
```

This ensures oversampling happens only on the training fold, never leaking into validation.

---

## 7) Thresholds, Calibration, and Costs

Most classifiers output probabilities; you can tune the decision threshold beyond 0.5.

- Precision‑Recall trade‑off: choose a threshold meeting a minimum recall requirement.
- Cost‑sensitive decision: minimize expected cost with a cost matrix.

Expected cost per decision with cost matrix $C$:
$$\mathbb{E}[\text{cost}] = \pi_1\,\text{FN\_rate}\,C_{FN} + \pi_0\,\text{FP\_rate}\,C_{FP}$$
where $\pi_1$ and $\pi_0$ are class prevalences.

Threshold tuning example:
```python
from sklearn.metrics import precision_recall_curve

proba = best_model.predict_proba(X_test)[:, 1]
prec, rec, thr = precision_recall_curve(y_test, proba)

# Example: pick threshold for recall >= 0.80 with highest precision
import numpy as np
mask = rec >= 0.80
best_idx = np.argmax(prec[mask])
best_thresh = thr[mask][best_idx]

y_hat = (proba >= best_thresh).astype(int)
```

Probability calibration helps when predicted probabilities are miscalibrated:
```python
from sklearn.calibration import CalibratedClassifierCV
cal_rf = CalibratedClassifierCV(best_model.named_steps['clf'], method='isotonic', cv=3)
cal_rf.fit(best_model.named_steps['pre'].transform(X_train), y_train)
cal_proba = cal_rf.predict_proba(best_model.named_steps['pre'].transform(X_test))[:, 1]
```

---

## 8) Model Explainability with SHAP (Global + Local)

SHAP attributes contributions to each feature per prediction. For tree models, use `TreeExplainer`.

```python
import shap

# Train on SMOTE data in transformed space
from sklearn.ensemble import RandomForestClassifier
rf_smote = RandomForestClassifier(random_state=42)
rf_smote.fit(X_train_smote, y_train_smote)

explainer = shap.TreeExplainer(rf_smote, X_train_smote)
shap_vals = explainer.shap_values(X_test_pp)[1]

# Global importance
feature_names = list(num) + preprocessor.named_transformers_['cat']['onehot']\
    .get_feature_names_out(cat).tolist()
shap.summary_plot(shap_vals, X_test_pp, feature_names=feature_names)

# Local explanation
i = 0
shap.force_plot(explainer.expected_value[1], shap_vals[i, :], X_test_pp[i, :], matplotlib=True)
```

Notes:
- Choose a reasonable background/sample for `TreeExplainer` to stabilize expectations.
- One‑hot names help interpret categorical contributions.
- For linear models, `LinearExplainer`; for general models, `KernelExplainer` (slower).

---

## 9) Evaluating Synthetic Data Quality

Descriptive checks:
- Compare distributions (KDE) of real vs. synthetic minority for key numerics.
- Visualize in 2D (t‑SNE/UMAP). Caution: t‑SNE distorts global structure; interpret locally.
- Compare correlation matrices of real vs. synthetic.
- Predictive check: can a classifier distinguish real vs. synthetic? Too‑high accuracy may indicate artifacts.

Illustration:
```python
# Simple discriminator
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
X_sanity = np.vstack([X_train_pp[y_train==1], X_train_smote[:sum(y_train==1)]])
y_sanity = np.hstack([np.zeros(sum(y_train==1)), np.ones(sum(y_train==1))])
Xs_tr, Xs_te, ys_tr, ys_te = train_test_split(X_sanity, y_sanity, test_size=0.3, random_state=42, stratify=y_sanity)
disc = RandomForestClassifier(random_state=42).fit(Xs_tr, ys_tr)
disc_acc = disc.score(Xs_te, ys_te)
```

Optional advanced distances (for research): Maximum Mean Discrepancy (MMD) between distributions.

---

## 10) Cross‑Validation and Hyperparameter Tuning

- Use `StratifiedKFold` to preserve class ratios per fold.
- Score with `average_precision` for PR‑AUC when classes are highly imbalanced.
- Keep oversampling inside the CV pipeline (see Section 6) so each fold is clean.

Grid search example already shown; you can also use `RandomizedSearchCV` for efficiency.

---

## 11) Robustness, Fairness, and Ethics

- Medical context requires careful false negative control (missed strokes) and clear communication of precision trade‑offs (false alarms).
- Check performance across subgroups (e.g., sex, age bands). Stratify evaluation to detect disparate impact.
- Avoid learning proxies for sensitive attributes; consider fairness metrics where appropriate.

---

## 12) Reproducibility & Performance Tips

- Fix seeds: `numpy`, `scikit-learn`, and any library RNGs.
- Capture environment: Python version and package versions (the notebook prints these).
- Use `n_jobs=-1` on CPU‑bound grid searches and ensembles.
- Cache transformations: `Pipeline(memory=...)` with a `joblib` cache directory.
- Save artifacts: metrics table (`results.csv`) and figures under `figures/`.

---

## 13) Minimal End‑to‑End Script

This script mirrors the core of the notebook in a compact form.

```python
import numpy as np, pandas as pd
from sklearn.model_selection import train_test_split, StratifiedKFold
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.impute import SimpleImputer
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, average_precision_score, roc_auc_score
from imblearn.over_sampling import SMOTE

df = pd.read_csv('healthcare-dataset-stroke-data.csv')
df = df.drop(columns=['id'])
df['gender'] = df['gender'].replace('Other', df['gender'].mode()[0])

X, y = df.drop('stroke', axis=1), df['stroke']
cat = X.select_dtypes(include=['object']).columns
num = X.select_dtypes(include=np.number).columns

num_tf = Pipeline([('imputer', SimpleImputer(strategy='mean')), ('scaler', StandardScaler())])
cat_tf = Pipeline([('imputer', SimpleImputer(strategy='most_frequent')), ('onehot', OneHotEncoder(handle_unknown='ignore'))])
pre = ColumnTransformer([('num', num_tf, num), ('cat', cat_tf, cat)])

X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
X_tr_pp = pre.fit_transform(X_tr)
X_te_pp = pre.transform(X_te)

sm = SMOTE(random_state=42)
X_tr_sm, y_tr_sm = sm.fit_resample(X_tr_pp, y_tr)

clf = LogisticRegression(max_iter=1000, random_state=42)
clf.fit(X_tr_sm, y_tr_sm)

proba = clf.predict_proba(X_te_pp)[:, 1]
print('ROC-AUC:', roc_auc_score(y_te, proba))
print('PR-AUC :', average_precision_score(y_te, proba))
print(classification_report(y_te, (proba>=0.5).astype(int)))
```

---

## 14) Practical Checklist

- Define objective: maximize minority recall/F1 under acceptable precision.
- Split first; oversample only the training fold.
- Use pipelines for preprocessing and keep feature names.
- Prefer PR‑AUC to compare models under heavy imbalance.
- Tune threshold and consider calibration for decision‑time reliability.
- Use SHAP to validate medical plausibility of drivers (e.g., age, glucose).
- Sanity‑check synthetic data; avoid artifacts.
- Log seeds, versions, metrics, and figures.

---

## 15) References & Further Reading

- Chawla et al. (2002), SMOTE: Synthetic Minority Over‑sampling Technique (JAIR).
- imbalanced‑learn documentation: https://imbalanced-learn.org
- SHAP documentation: https://shap.readthedocs.io
- scikit‑learn user guide: https://scikit-learn.org
- Saito & Rehmsmeier (2015), The Precision‑Recall Plot Is More Informative than the ROC Plot When Evaluating Binary Classifiers on Imbalanced Datasets.

---

## 16) Glossary

- Class Imbalance: Large difference in class frequencies.
- Oversampling: Increasing minority instances in training data.
- SMOTE: Synthetic data via neighbor interpolation.
- PR‑AUC: Area under precision‑recall curve; robust for rare events.
- SHAP: Additive feature attribution method for explanations.
