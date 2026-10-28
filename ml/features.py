"""
Wspólny kod cech: trening i serwis inferencji (FastAPI).

Zamienia pola kontraktu na dokładnie te kolumny, które dostaje model: 
dolicza cechy pochodne (rata, kwota/dochód, rata/dochód, 
flaga braku stażu), oznacza kolumny kategoryczne i zwraca
13 kolumn w stałej kolejności.Ten sam kod w treningu i na produkcji
chroni przed training-serving skew.

Uruchomiony bezpośrednio robi szybki sprawdzian na danych z parqueta.
"""


import pandas as pd
import numpy as np
from pathlib import Path


CATEGORICAL_COLUMNS = ["income_type", "education"]
FEATURE_COLUMNS = [
    "income",
    "credit_amount",
    "age_years",
    "employment_years",
    "income_type",
    "education",
    "ext_score_2",
    "ext_score_3",
    "num_installments",
    "installment_amount",
    "credit_to_income",
    "installment_to_income",
    "employment_missing"
]

REPO_ROOT = Path(__file__).resolve().parent.parent
DATA_PATH = REPO_ROOT / "data" / "processed" / "applications.parquet"


def add_features(df):
    """
    Dolicza cechy pochodne i zwraca 13 kolumn modelowych w stałej kolejności.
    """
    df = df.copy()
    for col in CATEGORICAL_COLUMNS:
        df[col] = df[col].astype("category")

    df['installment_amount'] = df['credit_amount'] / df['num_installments']
    df['credit_to_income'] = df['credit_amount'] / df['income']
    df['installment_to_income'] = df['installment_amount'] / df['income']
    df['employment_missing'] = df['employment_years'].isna().astype(int)

    return df[FEATURE_COLUMNS]

def main():
    df = pd.read_parquet(DATA_PATH)
    df = add_features(df)
    df.info()
    print(df['employment_missing'].sum())

    new_cols = ['installment_amount', 'credit_to_income', 'installment_to_income', 'employment_missing']
    print(np.isinf(df[new_cols]).sum())

if __name__ == "__main__":
    main()
