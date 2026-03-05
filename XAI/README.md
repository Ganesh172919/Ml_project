# Handling Class Imbalance with Oversampling & XAI (Stroke Prediction)

This repository demonstrates how to handle severe class imbalance using advanced oversampling (SMOTE) and how to validate models with Explainable AI (SHAP). The project uses the Stroke Prediction dataset and walks through EDA, preprocessing with scikit-learn pipelines, model training/evaluation, oversampling, and model explainability.

- Notebook: `Handling_Class_Imbalance_XAI.ipynb`
- Dataset: `healthcare-dataset-stroke-data.csv` (Kaggle – place alongside the notebook)
- Figures/Artifacts: `figures/`
- In-depth learning: `LEARNING_GUIDE.md`

## Quick Start (Windows PowerShell)

Prerequisites: Python 3.9+ and Git.

```powershell
# 1) Create and activate a virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# 2) Upgrade pip
python -m pip install -U pip

# 3) Install dependencies
python -m pip install numpy pandas matplotlib seaborn scikit-learn imbalanced-learn shap ipywidgets

# 4) (Optional) Enable Jupyter widgets support
jupyter nbextension enable --py widgetsnbextension
```

## Run the Notebook

1. Open VS Code and this folder.
2. Open `Handling_Class_Imbalance_XAI.ipynb`.
3. Select the `.venv` Python interpreter.
4. Ensure `healthcare-dataset-stroke-data.csv` is present in the repo root.
5. Run cells top-to-bottom. Plots and artifacts save to `figures/` and `results.csv` at root.

## What You’ll See

- Baseline models (Logistic Regression, Random Forest) on imbalanced data with proper metrics (ROC-AUC, PR-AUC, recall/F1 for minority).
- SMOTE applied correctly to training data only, with distribution checks and feature-distribution comparisons.
- Side-by-side performance comparison: baseline vs. SMOTE.
- XAI with SHAP (global summary and local force plots) to validate learned patterns.
- Sanity checks: t-SNE visualization, probability comparisons, and correlation heatmaps for real vs. synthetic samples.

## Project Structure

```
.
├── Handling_Class_Imbalance_XAI.ipynb   # Main walkthrough notebook
├── healthcare-dataset-stroke-data.csv    # Dataset (add locally)
├── figures/                              # Saved plots
├── project_documentation/
│   └── key_concepts/                     # Topic-focused notes (optional)
│       ├── numpy_pandas.md
│       ├── oversampling_techniques.md
│       ├── python_basics.md
│       ├── scikit_learn_guide.md
│       └── xai_methods.md
├── LEARNING_GUIDE.md                     # One-file condensed concepts + code
└── README.md
```

## Dependencies

- numpy, pandas, matplotlib, seaborn
- scikit-learn, imbalanced-learn
- shap, ipywidgets

If you prefer conda, create an environment and install the same packages via `conda` or `pip`.

## Reproducing Results

Run the entire notebook. Key figures are saved to `figures/`:

- `class_distribution.png`
- `baseline_Logistic Regression_cm.png`, `baseline_Random Forest_cm.png`
- `baseline_curves.png`, `smote_class_distribution.png`, `smote_feature_distributions.png`
- `smote_comparison.png`, `shap_summary_plot.png`, SHAP force plots
- `tsne_visualization.png`, `predicted_probabilities.png`, `correlation_comparison.png`

`results.csv` contains the baseline vs. SMOTE metric table.

## Troubleshooting

- SHAP plots blank or error: ensure `shap` installed; for force plots inside VS Code, prefer `matplotlib=True` versions included in the notebook, and keep `feature_names` aligned.
- Import errors: confirm the active interpreter is the `.venv` you created.
- Imbalanced-learn missing: `python -m pip install imbalanced-learn`.

## Learn More

For a single-file deep dive with code snippets and explanations, read `LEARNING_GUIDE.md`.

Dataset source: Kaggle “Stroke Prediction Dataset”. Please download and place the CSV in the repo root.

