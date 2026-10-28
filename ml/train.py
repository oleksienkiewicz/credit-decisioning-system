"""
Trening modelu ryzyka kredytowego.
Uruchamianie z korzenia repo: python -m ml.train
"""

from datetime import datetime, timezone
from pathlib import Path

import joblib
import pandas as pd
from lightgbm import LGBMClassifier
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import FunctionTransformer

from ml.features import add_features

REPO_ROOT = Path(__file__).resolve().parent.parent
DATA_PATH = REPO_ROOT / "data" / "processed" / "applications.parquet"
ARTIFACTS_DIR = REPO_ROOT / "artifacts"

MODEL_VERSION = "v1"
TARGET = "target"
TEST_SIZE = 0.2
RANDOM_STATE = 42


def load_data():
    """Wczytuje parquet i rozdziela go na X (9 pól kontraktu) i y (target)."""
    df = pd.read_parquet(DATA_PATH)
    X = df.drop(columns=[TARGET])
    y = df[TARGET]

    return X, y


def split_data(X, y):
    """Dzieli dane na train/test ze stratyfikacją po targecie."""
    X_train, X_test, y_train, y_test = train_test_split(X, y, stratify=y, test_size=TEST_SIZE, random_state=RANDOM_STATE)

    return X_train, X_test, y_train, y_test


def build_pipeline():
    """Zwraca NIEWYTRENOWANY pipeline: cechy pochodne -> LightGBM."""
    model = LGBMClassifier(random_state = RANDOM_STATE, verbose = -1)
    features = FunctionTransformer(add_features)
    
    return Pipeline([("features", features), ("model", model)])


def evaluate(pipeline, X_test, y_test):
    """Liczy metryki na teście i zwraca je jako słownik."""
    metrics = {}
    y_pred_proba = pipeline.predict_proba(X_test)[:, 1]
    auc = roc_auc_score(y_test, y_pred_proba)
    gini = 2 * auc - 1
    mean_pd = y_pred_proba.mean()
    default_rate = y_test.mean()
    metrics["auc"] = float(auc)
    metrics["gini"] = float(gini)
    metrics["mean_pd"] = float(mean_pd)
    metrics["default_rate"] = float(default_rate)

    return metrics


def save_artifact(pipeline, metrics, input_columns):
    """Zapisuje pipeline z metadanymi jako jeden plik i zwraca jego ścieżkę."""
    ARTIFACTS_DIR.mkdir(exist_ok=True, parents=True)

    artifact_dict = {
        "pipeline": pipeline,
        "metrics": metrics,
        "input_columns": input_columns,
        "model_version": MODEL_VERSION,
        "trained_at": datetime.now(timezone.utc).isoformat()
    }

    path = ARTIFACTS_DIR / f"credit_model_{MODEL_VERSION}.joblib"
    joblib.dump(artifact_dict, path)

    return path


def check_artifact(path, X_sample):
    """Symulacja FastAPI: wczytuje artefakt i liczy PD dla kilku surowych wierszy."""
    artifact = joblib.load(path)
    pipeline = artifact["pipeline"]
    y_pred_sample = pipeline.predict_proba(X_sample)[:, 1]

    print(f"Sample predictions: {y_pred_sample}")


def main():
    X, y = load_data()
    X_train, X_test, y_train, y_test = split_data(X, y)

    pipeline = build_pipeline()
    pipeline.fit(X_train, y_train)

    metrics = evaluate(pipeline, X_test, y_test)
    print(f"Metrics: {metrics}")

    path = save_artifact(pipeline, metrics, list(X.columns))
    print(f"Artifact path: {path}")

    check_artifact(path, X_test.head(3))


if __name__ == "__main__":
    main()