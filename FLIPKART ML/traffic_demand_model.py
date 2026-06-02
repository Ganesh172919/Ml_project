"""
Traffic Demand Prediction - Gridlock Hackathon 2.0 (Flipkart)
=============================================================
High-accuracy ensemble model: LightGBM + XGBoost + CatBoost
Metric: score = max(0, 100 * r2_score(actual, predicted))

Author: Auto-generated for competition submission
"""

import warnings
warnings.filterwarnings("ignore")

import numpy as np
import pandas as pd
from sklearn.model_selection import KFold
from sklearn.metrics import r2_score
from sklearn.preprocessing import LabelEncoder
import lightgbm as lgb
import xgboost as xgb
import catboost as cb
from scipy.optimize import minimize
import optuna
optuna.logging.set_verbosity(optuna.logging.WARNING)
import os
import time
import gc

# ============================================================
# CONFIGURATION
# ============================================================
SEED = 42
N_FOLDS = 5
DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dataset")
OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))

np.random.seed(SEED)

# ============================================================
# 1. GEOHASH DECODER (Pure Python - no external dependency)
# ============================================================
BASE32 = "0123456789bcdefghjkmnpqrstuvwxyz"
BASE32_MAP = {c: i for i, c in enumerate(BASE32)}

def decode_geohash(geohash_str):
    """Decode a geohash string to (latitude, longitude) centroid."""
    lat_interval = [-90.0, 90.0]
    lon_interval = [-180.0, 180.0]
    is_even = True
    for char in geohash_str:
        cd = BASE32_MAP.get(char, 0)
        for mask in [16, 8, 4, 2, 1]:
            if is_even:
                mid = (lon_interval[0] + lon_interval[1]) / 2
                if cd & mask:
                    lon_interval[0] = mid
                else:
                    lon_interval[1] = mid
            else:
                mid = (lat_interval[0] + lat_interval[1]) / 2
                if cd & mask:
                    lat_interval[0] = mid
                else:
                    lat_interval[1] = mid
            is_even = not is_even
    lat = (lat_interval[0] + lat_interval[1]) / 2
    lon = (lon_interval[0] + lon_interval[1]) / 2
    return lat, lon


def decode_geohash_vectorized(geohash_series):
    """Vectorized geohash decoding for a pandas Series."""
    unique_hashes = geohash_series.unique()
    decoded = {gh: decode_geohash(gh) for gh in unique_hashes}
    lats = geohash_series.map(lambda x: decoded[x][0])
    lons = geohash_series.map(lambda x: decoded[x][1])
    return lats.astype(np.float32), lons.astype(np.float32)


# ============================================================
# 2. DATA LOADING
# ============================================================
def load_data():
    """Load train, test, and sample submission data."""
    print("=" * 60)
    print("LOADING DATA")
    print("=" * 60)
    
    train = pd.read_csv(os.path.join(DATA_DIR, "train.csv"))
    test = pd.read_csv(os.path.join(DATA_DIR, "test.csv"))
    sample_sub = pd.read_csv(os.path.join(DATA_DIR, "sample_submission.csv"))
    
    print(f"Train shape: {train.shape}")
    print(f"Test shape:  {test.shape}")
    print(f"Sample sub:  {sample_sub.shape}")
    print(f"\nTrain columns: {list(train.columns)}")
    print(f"Test columns:  {list(test.columns)}")
    print(f"\nTarget (demand) stats:\n{train['demand'].describe()}")
    print(f"\nMissing values in train:\n{train.isnull().sum()}")
    print(f"\nMissing values in test:\n{test.isnull().sum()}")
    
    return train, test, sample_sub


# ============================================================
# 3. FEATURE ENGINEERING (The Core of High R²)
# ============================================================
def engineer_features(train, test):
    """Create all features for train and test simultaneously."""
    print("\n" + "=" * 60)
    print("FEATURE ENGINEERING")
    print("=" * 60)
    
    target = train["demand"].values.copy()
    train_idx = train["Index"].values.copy()
    test_idx = test["Index"].values.copy()
    
    # Combine for consistent feature engineering
    train["is_train"] = 1
    test["is_train"] = 0
    if "demand" not in test.columns:
        test["demand"] = np.nan
    
    df = pd.concat([train, test], axis=0, ignore_index=True)
    print(f"Combined shape: {df.shape}")
    
    # ---- 3a. Geohash Decoding ----
    print("  [1/8] Decoding geohash to lat/lon...")
    df["latitude"], df["longitude"] = decode_geohash_vectorized(df["geohash"])
    
    # Geohash prefix features (hierarchical geographic grouping)
    df["geohash_3"] = df["geohash"].str[:3]
    df["geohash_4"] = df["geohash"].str[:4]
    df["geohash_5"] = df["geohash"].str[:5]
    
    # ---- 3b. Timestamp Parsing ----
    print("  [2/8] Parsing timestamps...")
    ts_split = df["timestamp"].str.split(":", expand=True)
    df["hour"] = ts_split[0].astype(int)
    df["minute"] = ts_split[1].astype(int)
    df["time_slot"] = df["hour"] * 60 + df["minute"]  # minutes since midnight
    
    # Cyclical time encoding (hour wraps around 24, minute wraps around 60)
    df["hour_sin"] = np.sin(2 * np.pi * df["hour"] / 24).astype(np.float32)
    df["hour_cos"] = np.cos(2 * np.pi * df["hour"] / 24).astype(np.float32)
    df["minute_sin"] = np.sin(2 * np.pi * df["minute"] / 60).astype(np.float32)
    df["minute_cos"] = np.cos(2 * np.pi * df["minute"] / 60).astype(np.float32)
    df["timeslot_sin"] = np.sin(2 * np.pi * df["time_slot"] / 1440).astype(np.float32)
    df["timeslot_cos"] = np.cos(2 * np.pi * df["time_slot"] / 1440).astype(np.float32)
    
    # ---- 3c. Day Features ----
    print("  [3/8] Creating day features...")
    df["day_of_week"] = df["day"] % 7
    df["is_weekend"] = (df["day_of_week"] >= 5).astype(np.int8)
    
    # Day cyclical
    df["dow_sin"] = np.sin(2 * np.pi * df["day_of_week"] / 7).astype(np.float32)
    df["dow_cos"] = np.cos(2 * np.pi * df["day_of_week"] / 7).astype(np.float32)
    
    # Peak hour flags
    df["is_morning_rush"] = ((df["hour"] >= 7) & (df["hour"] <= 9)).astype(np.int8)
    df["is_evening_rush"] = ((df["hour"] >= 17) & (df["hour"] <= 20)).astype(np.int8)
    df["is_night"] = ((df["hour"] >= 22) | (df["hour"] <= 5)).astype(np.int8)
    df["is_peak"] = (df["is_morning_rush"] | df["is_evening_rush"]).astype(np.int8)
    
    # ---- 3d. Categorical Encoding ----
    print("  [4/8] Encoding categoricals...")
    
    # Fill missing categoricals
    df["RoadType"] = df["RoadType"].fillna("Unknown")
    df["Weather"] = df["Weather"].fillna("Unknown")
    df["LargeVehicles"] = df["LargeVehicles"].fillna("Unknown")
    df["Landmarks"] = df["Landmarks"].fillna("Unknown")
    
    # Binary encode
    df["LargeVehicles_enc"] = (df["LargeVehicles"] == "Allowed").astype(np.int8)
    df["Landmarks_enc"] = (df["Landmarks"] == "Yes").astype(np.int8)
    
    # Label encode categorical columns
    cat_cols = ["RoadType", "Weather", "geohash_3", "geohash_4", "geohash_5"]
    label_encoders = {}
    for col in cat_cols:
        le = LabelEncoder()
        df[col + "_le"] = le.fit_transform(df[col].astype(str))
        label_encoders[col] = le
    
    # Geohash label encoding  
    le_geo = LabelEncoder()
    df["geohash_le"] = le_geo.fit_transform(df["geohash"])
    
    # ---- 3e. Temperature Handling ----
    print("  [5/8] Handling temperature...")
    
    # Impute temperature with median per (geohash_4, Weather)
    temp_median_geo_weather = df.groupby(["geohash_4", "Weather"])["Temperature"].transform("median")
    temp_median_weather = df.groupby("Weather")["Temperature"].transform("median")
    temp_global_median = df["Temperature"].median()
    
    df["Temperature"] = df["Temperature"].fillna(temp_median_geo_weather)
    df["Temperature"] = df["Temperature"].fillna(temp_median_weather)
    df["Temperature"] = df["Temperature"].fillna(temp_global_median)
    
    df["temp_missing"] = df["Temperature"].isna().astype(np.int8)  # will be 0 after impute, but keep for safety
    
    # Temperature bins
    df["temp_bin"] = pd.cut(df["Temperature"], bins=10, labels=False).fillna(0).astype(np.int8)
    
    # ---- 3f. Interaction Features ----
    print("  [6/8] Creating interaction features...")
    df["lanes_x_peak"] = df["NumberofLanes"] * df["is_peak"]
    df["lanes_x_weekend"] = df["NumberofLanes"] * df["is_weekend"]
    df["landmark_x_peak"] = df["Landmarks_enc"] * df["is_peak"]
    df["lat_x_lon"] = df["latitude"] * df["longitude"]
    df["temp_x_peak"] = df["Temperature"] * df["is_peak"]
    
    # ---- 3g. Target Encoding (with KFold leak prevention) ----
    print("  [7/8] Target encoding (KFold cross-validated)...")
    
    train_mask = df["is_train"] == 1
    
    # Target encode high-cardinality features using KFold on training data
    target_encode_cols = ["geohash", "geohash_4", "geohash_5"]
    
    for col in target_encode_cols:
        col_name = f"{col}_target_enc"
        df[col_name] = np.nan
        
        train_df = df[train_mask].copy()
        test_df = df[~train_mask].copy()
        
        # For test data: use global mean per category from all training data
        global_means = train_df.groupby(col)["demand"].mean()
        overall_mean = train_df["demand"].mean()
        
        # Smoothed target encoding for test
        counts = train_df.groupby(col)["demand"].count()
        smoothing_factor = 20
        smooth_means = (counts * global_means + smoothing_factor * overall_mean) / (counts + smoothing_factor)
        
        df.loc[~train_mask, col_name] = test_df[col].map(smooth_means).fillna(overall_mean).values
        
        # For train data: KFold to prevent leakage
        kf = KFold(n_splits=N_FOLDS, shuffle=True, random_state=SEED)
        train_indices = df[train_mask].index
        
        for fold_train_idx, fold_val_idx in kf.split(train_indices):
            actual_train_idx = train_indices[fold_train_idx]
            actual_val_idx = train_indices[fold_val_idx]
            
            fold_means = df.loc[actual_train_idx].groupby(col)["demand"].mean()
            fold_counts = df.loc[actual_train_idx].groupby(col)["demand"].count()
            fold_smooth = (fold_counts * fold_means + smoothing_factor * overall_mean) / (fold_counts + smoothing_factor)
            
            df.loc[actual_val_idx, col_name] = df.loc[actual_val_idx, col].map(fold_smooth).fillna(overall_mean).values
    
    # Aggregation features: mean demand per geohash at different time granularities
    # (These use training data only, mapped to test)
    agg_features = {
        "geohash": ["mean", "std", "median", "min", "max", "count"],
        "geohash_4": ["mean", "std"],
        "geohash_3": ["mean", "std"],
    }
    
    train_only = df[train_mask]
    
    for group_col, agg_funcs in agg_features.items():
        agg = train_only.groupby(group_col)["demand"].agg(agg_funcs)
        agg.columns = [f"demand_{group_col}_{func}" for func in agg_funcs]
        df = df.merge(agg, on=group_col, how="left")
    
    # Time-based aggregations
    time_aggs = [
        (["geohash", "hour"], ["mean", "std"]),
        (["geohash", "day_of_week"], ["mean"]),
        (["geohash", "is_peak"], ["mean"]),
        (["geohash_4", "hour"], ["mean"]),
        (["RoadType", "hour"], ["mean"]),
    ]
    
    for group_cols, agg_funcs in time_aggs:
        col_name_prefix = "_".join(group_cols)
        agg = train_only.groupby(group_cols)["demand"].agg(agg_funcs)
        agg.columns = [f"demand_{col_name_prefix}_{func}" for func in agg_funcs]
        agg = agg.reset_index()
        df = df.merge(agg, on=group_cols, how="left")
    
    # Fill NaN from aggregations
    for col in df.columns:
        if col.startswith("demand_") and col != "demand":
            df[col] = df[col].fillna(df[col].median())
    
    # ---- 3h. Final Feature Selection ----
    print("  [8/8] Selecting final features...")
    
    drop_cols = [
        "Index", "geohash", "timestamp", "demand", "is_train",
        "RoadType", "Weather", "LargeVehicles", "Landmarks",
        "geohash_3", "geohash_4", "geohash_5",
    ]
    
    feature_cols = [c for c in df.columns if c not in drop_cols]
    print(f"\n  Total features: {len(feature_cols)}")
    print(f"  Features: {feature_cols[:20]}...")
    
    X_train = df[train_mask][feature_cols].values.astype(np.float32)
    X_test = df[~train_mask][feature_cols].values.astype(np.float32)
    
    # Handle any remaining NaN
    X_train = np.nan_to_num(X_train, nan=0.0)
    X_test = np.nan_to_num(X_test, nan=0.0)
    
    print(f"\n  X_train: {X_train.shape}, y_train: {target.shape}")
    print(f"  X_test:  {X_test.shape}")
    
    return X_train, target, X_test, train_idx, test_idx, feature_cols


# ============================================================
# 4. MODEL TRAINING WITH OPTUNA HYPERPARAMETER TUNING
# ============================================================

def train_lgb_with_optuna(X, y, n_trials=40):
    """Train LightGBM with Optuna hyperparameter optimization."""
    print("\n" + "=" * 60)
    print("TRAINING LightGBM (with Optuna)")
    print("=" * 60)
    
    best_params = {}
    
    def objective(trial):
        params = {
            "objective": "regression",
            "metric": "rmse",
            "verbosity": -1,
            "boosting_type": "gbdt",
            "n_estimators": trial.suggest_int("n_estimators", 500, 3000),
            "learning_rate": trial.suggest_float("learning_rate", 0.005, 0.1, log=True),
            "max_depth": trial.suggest_int("max_depth", 4, 12),
            "num_leaves": trial.suggest_int("num_leaves", 20, 256),
            "min_child_samples": trial.suggest_int("min_child_samples", 5, 100),
            "subsample": trial.suggest_float("subsample", 0.5, 1.0),
            "colsample_bytree": trial.suggest_float("colsample_bytree", 0.3, 1.0),
            "reg_alpha": trial.suggest_float("reg_alpha", 1e-8, 10.0, log=True),
            "reg_lambda": trial.suggest_float("reg_lambda", 1e-8, 10.0, log=True),
            "min_split_gain": trial.suggest_float("min_split_gain", 0.0, 1.0),
            "random_state": SEED,
        }
        
        kf = KFold(n_splits=N_FOLDS, shuffle=True, random_state=SEED)
        scores = []
        
        for train_idx, val_idx in kf.split(X):
            X_tr, X_val = X[train_idx], X[val_idx]
            y_tr, y_val = y[train_idx], y[val_idx]
            
            model = lgb.LGBMRegressor(**params)
            model.fit(
                X_tr, y_tr,
                eval_set=[(X_val, y_val)],
                callbacks=[lgb.early_stopping(50, verbose=False), lgb.log_evaluation(0)]
            )
            
            pred = model.predict(X_val)
            pred = np.clip(pred, 0, None)  # demand cannot be negative
            scores.append(r2_score(y_val, pred))
        
        return np.mean(scores)
    
    study = optuna.create_study(direction="maximize", sampler=optuna.samplers.TPESampler(seed=SEED))
    study.optimize(objective, n_trials=n_trials, show_progress_bar=True)
    
    best_params = study.best_params
    best_params.update({
        "objective": "regression",
        "metric": "rmse",
        "verbosity": -1,
        "boosting_type": "gbdt",
        "random_state": SEED,
    })
    
    print(f"\n  Best LGB CV R²: {study.best_value:.6f}")
    print(f"  Best params: {best_params}")
    
    return best_params, study.best_value


def train_xgb_with_optuna(X, y, n_trials=40):
    """Train XGBoost with Optuna hyperparameter optimization."""
    print("\n" + "=" * 60)
    print("TRAINING XGBoost (with Optuna)")
    print("=" * 60)
    
    def objective(trial):
        params = {
            "objective": "reg:squarederror",
            "n_estimators": trial.suggest_int("n_estimators", 500, 3000),
            "learning_rate": trial.suggest_float("learning_rate", 0.005, 0.1, log=True),
            "max_depth": trial.suggest_int("max_depth", 4, 12),
            "min_child_weight": trial.suggest_int("min_child_weight", 1, 50),
            "subsample": trial.suggest_float("subsample", 0.5, 1.0),
            "colsample_bytree": trial.suggest_float("colsample_bytree", 0.3, 1.0),
            "reg_alpha": trial.suggest_float("reg_alpha", 1e-8, 10.0, log=True),
            "reg_lambda": trial.suggest_float("reg_lambda", 1e-8, 10.0, log=True),
            "gamma": trial.suggest_float("gamma", 0.0, 5.0),
            "random_state": SEED,
            "tree_method": "hist",
            "verbosity": 0,
        }
        
        kf = KFold(n_splits=N_FOLDS, shuffle=True, random_state=SEED)
        scores = []
        
        for train_idx, val_idx in kf.split(X):
            X_tr, X_val = X[train_idx], X[val_idx]
            y_tr, y_val = y[train_idx], y[val_idx]
            
            model = xgb.XGBRegressor(**params)
            model.fit(
                X_tr, y_tr,
                eval_set=[(X_val, y_val)],
                verbose=False,
            )
            
            pred = model.predict(X_val)
            pred = np.clip(pred, 0, None)
            scores.append(r2_score(y_val, pred))
        
        return np.mean(scores)
    
    study = optuna.create_study(direction="maximize", sampler=optuna.samplers.TPESampler(seed=SEED))
    study.optimize(objective, n_trials=n_trials, show_progress_bar=True)
    
    best_params = study.best_params
    best_params.update({
        "objective": "reg:squarederror",
        "random_state": SEED,
        "tree_method": "hist",
        "verbosity": 0,
    })
    
    print(f"\n  Best XGB CV R²: {study.best_value:.6f}")
    print(f"  Best params: {best_params}")
    
    return best_params, study.best_value


def train_catboost_with_optuna(X, y, n_trials=30):
    """Train CatBoost with Optuna hyperparameter optimization."""
    print("\n" + "=" * 60)
    print("TRAINING CatBoost (with Optuna)")
    print("=" * 60)
    
    def objective(trial):
        params = {
            "iterations": trial.suggest_int("iterations", 500, 3000),
            "learning_rate": trial.suggest_float("learning_rate", 0.005, 0.1, log=True),
            "depth": trial.suggest_int("depth", 4, 10),
            "l2_leaf_reg": trial.suggest_float("l2_leaf_reg", 1e-3, 10.0, log=True),
            "bagging_temperature": trial.suggest_float("bagging_temperature", 0.0, 10.0),
            "random_strength": trial.suggest_float("random_strength", 0.0, 10.0),
            "border_count": trial.suggest_int("border_count", 32, 255),
            "min_data_in_leaf": trial.suggest_int("min_data_in_leaf", 1, 50),
            "random_seed": SEED,
            "verbose": 0,
            "loss_function": "RMSE",
            "eval_metric": "R2",
        }
        
        kf = KFold(n_splits=N_FOLDS, shuffle=True, random_state=SEED)
        scores = []
        
        for train_idx, val_idx in kf.split(X):
            X_tr, X_val = X[train_idx], X[val_idx]
            y_tr, y_val = y[train_idx], y[val_idx]
            
            model = cb.CatBoostRegressor(**params)
            model.fit(
                X_tr, y_tr,
                eval_set=(X_val, y_val),
                early_stopping_rounds=50,
                verbose=0,
            )
            
            pred = model.predict(X_val)
            pred = np.clip(pred, 0, None)
            scores.append(r2_score(y_val, pred))
        
        return np.mean(scores)
    
    study = optuna.create_study(direction="maximize", sampler=optuna.samplers.TPESampler(seed=SEED))
    study.optimize(objective, n_trials=n_trials, show_progress_bar=True)
    
    best_params = study.best_params
    best_params.update({
        "random_seed": SEED,
        "verbose": 0,
        "loss_function": "RMSE",
        "eval_metric": "R2",
    })
    
    print(f"\n  Best CB CV R²: {study.best_value:.6f}")
    print(f"  Best params: {best_params}")
    
    return best_params, study.best_value


# ============================================================
# 5. FULL CV TRAINING + OOF PREDICTIONS
# ============================================================

def train_model_cv(X, y, X_test, model_type, params):
    """Train model with KFold CV and return OOF + test predictions."""
    kf = KFold(n_splits=N_FOLDS, shuffle=True, random_state=SEED)
    
    oof_preds = np.zeros(len(X))
    test_preds = np.zeros(len(X_test))
    scores = []
    importances = np.zeros(X.shape[1])
    
    for fold, (train_idx, val_idx) in enumerate(kf.split(X)):
        X_tr, X_val = X[train_idx], X[val_idx]
        y_tr, y_val = y[train_idx], y[val_idx]
        
        if model_type == "lgb":
            model = lgb.LGBMRegressor(**params)
            model.fit(
                X_tr, y_tr,
                eval_set=[(X_val, y_val)],
                callbacks=[lgb.early_stopping(100, verbose=False), lgb.log_evaluation(0)]
            )
            importances += model.feature_importances_ / N_FOLDS
            
        elif model_type == "xgb":
            model = xgb.XGBRegressor(**params)
            model.fit(
                X_tr, y_tr,
                eval_set=[(X_val, y_val)],
                verbose=False,
            )
            importances += model.feature_importances_ / N_FOLDS
            
        elif model_type == "cb":
            model = cb.CatBoostRegressor(**params)
            model.fit(
                X_tr, y_tr,
                eval_set=(X_val, y_val),
                early_stopping_rounds=100,
                verbose=0,
            )
            importances += model.feature_importances_ / N_FOLDS
        
        val_pred = model.predict(X_val)
        val_pred = np.clip(val_pred, 0, None)
        oof_preds[val_idx] = val_pred
        
        fold_score = r2_score(y_val, val_pred)
        scores.append(fold_score)
        
        test_preds += model.predict(X_test) / N_FOLDS
        
        print(f"    Fold {fold + 1}: R² = {fold_score:.6f}")
    
    test_preds = np.clip(test_preds, 0, None)
    mean_score = np.mean(scores)
    print(f"    >>> Mean CV R²: {mean_score:.6f} (±{np.std(scores):.6f})")
    
    return oof_preds, test_preds, mean_score, importances


# ============================================================
# 6. ENSEMBLE WEIGHT OPTIMIZATION
# ============================================================

def optimize_ensemble_weights(y_true, oof_predictions_list):
    """Find optimal weights for ensemble using scipy minimize."""
    print("\n" + "=" * 60)
    print("OPTIMIZING ENSEMBLE WEIGHTS")
    print("=" * 60)
    
    n_models = len(oof_predictions_list)
    
    def neg_r2(weights):
        weighted_pred = sum(w * p for w, p in zip(weights, oof_predictions_list))
        weighted_pred = np.clip(weighted_pred, 0, None)
        return -r2_score(y_true, weighted_pred)
    
    # Constraint: weights sum to 1
    constraints = {"type": "eq", "fun": lambda w: np.sum(w) - 1}
    bounds = [(0, 1)] * n_models
    
    # Try multiple initial points for robustness
    best_result = None
    best_score = -np.inf
    
    for _ in range(50):
        x0 = np.random.dirichlet(np.ones(n_models))
        result = minimize(neg_r2, x0, method="SLSQP", bounds=bounds, constraints=constraints)
        if -result.fun > best_score:
            best_score = -result.fun
            best_result = result
    
    weights = best_result.x
    print(f"  Optimal weights: {weights}")
    print(f"  Ensemble R²: {best_score:.6f}")
    
    return weights


# ============================================================
# 7. MAIN PIPELINE
# ============================================================

def main():
    total_start = time.time()
    
    # Load data
    train, test, sample_sub = load_data()
    
    # Feature engineering
    X_train, y_train, X_test, train_idx_vals, test_idx_vals, feature_cols = engineer_features(train, test)
    
    # Free memory
    del train, test
    gc.collect()
    
    # ---- Hyperparameter Tuning ----
    print("\n" + "#" * 60)
    print("PHASE 1: HYPERPARAMETER TUNING (Optuna)")
    print("#" * 60)
    
    lgb_params, lgb_score = train_lgb_with_optuna(X_train, y_train, n_trials=40)
    xgb_params, xgb_score = train_xgb_with_optuna(X_train, y_train, n_trials=40)
    cb_params, cb_score = train_catboost_with_optuna(X_train, y_train, n_trials=30)
    
    # ---- Full CV Training ----
    print("\n" + "#" * 60)
    print("PHASE 2: FULL CV TRAINING WITH BEST PARAMS")
    print("#" * 60)
    
    print("\n--- LightGBM ---")
    lgb_oof, lgb_test, lgb_cv, lgb_imp = train_model_cv(X_train, y_train, X_test, "lgb", lgb_params)
    
    print("\n--- XGBoost ---")
    xgb_oof, xgb_test, xgb_cv, xgb_imp = train_model_cv(X_train, y_train, X_test, "xgb", xgb_params)
    
    print("\n--- CatBoost ---")
    cb_oof, cb_test, cb_cv, cb_imp = train_model_cv(X_train, y_train, X_test, "cb", cb_params)
    
    # ---- Ensemble ----
    weights = optimize_ensemble_weights(y_train, [lgb_oof, xgb_oof, cb_oof])
    
    # Final ensemble predictions
    final_test = weights[0] * lgb_test + weights[1] * xgb_test + weights[2] * cb_test
    final_test = np.clip(final_test, 0, None)
    
    # Ensemble OOF for final score
    final_oof = weights[0] * lgb_oof + weights[1] * xgb_oof + weights[2] * cb_oof
    final_oof = np.clip(final_oof, 0, None)
    final_r2 = r2_score(y_train, final_oof)
    
    print("\n" + "=" * 60)
    print("FINAL RESULTS")
    print("=" * 60)
    print(f"  LightGBM CV R²:  {lgb_cv:.6f}")
    print(f"  XGBoost CV R²:   {xgb_cv:.6f}")
    print(f"  CatBoost CV R²:  {cb_cv:.6f}")
    print(f"  Ensemble CV R²:  {final_r2:.6f}")
    print(f"  Competition Score: {max(0, 100 * final_r2):.4f}")
    
    # ---- Feature Importance ----
    print("\n  Top 20 Features (LightGBM importance):")
    imp_df = pd.DataFrame({"feature": feature_cols, "importance": lgb_imp})
    imp_df = imp_df.sort_values("importance", ascending=False).head(20)
    for _, row in imp_df.iterrows():
        print(f"    {row['feature']:40s} {row['importance']:.4f}")
    
    # ---- Generate Submission ----
    print("\n" + "=" * 60)
    print("GENERATING SUBMISSION")
    print("=" * 60)
    
    submission = pd.DataFrame({
        "Index": test_idx_vals,
        "demand": final_test
    })
    
    sub_path = os.path.join(OUTPUT_DIR, "submission.csv")
    submission.to_csv(sub_path, index=False)
    
    print(f"  Submission shape: {submission.shape}")
    print(f"  Demand stats:\n{submission['demand'].describe()}")
    print(f"  Any NaN: {submission['demand'].isna().sum()}")
    print(f"  Saved to: {sub_path}")
    
    # Validate submission format
    assert submission.shape[0] == 41778, f"Expected 41778 rows, got {submission.shape[0]}"
    assert list(submission.columns) == ["Index", "demand"], f"Wrong columns: {list(submission.columns)}"
    assert submission["demand"].isna().sum() == 0, "NaN values in predictions!"
    print("\n  ✓ Submission validation passed!")
    
    total_time = time.time() - total_start
    print(f"\n  Total runtime: {total_time / 60:.1f} minutes")
    print("\nDone! Upload 'submission.csv' to HackerEarth.")


if __name__ == "__main__":
    main()
