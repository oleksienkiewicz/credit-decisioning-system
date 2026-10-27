"""
Przygotowanie danych treningowych z Home Credit Default Risk.

Wczytuje surowy application_train.csv, nadaje kolumnom nazwy kontraktu
i tłumaczy je na ludzkie jednostki (wiek i staż w latach, liczba rat
zamiast raty). Wynik zapisuje do data/processed/applications.parquet.
Uruchamiany raz, offline: python -m ml.prepare_data

Świadomie NIE robi: imputacji, skalowania, kodowania kategorii, cech
pochodnych, flagi braku stażu ani podziału na train/test. To należy
do kodu cech i treningu, bo musi działać identycznie na produkcji.
"""

import pandas as pd
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
RAW_PATH = REPO_ROOT / "data" / "raw" / "application_train.csv"
OUTPUT_PATH = REPO_ROOT / "data" / "processed" / "applications.parquet"

COLUMNS = {
        'AMT_INCOME_TOTAL': 'income',
        'AMT_CREDIT': 'credit_amount',
        'AMT_ANNUITY': 'annuity',
        'DAYS_BIRTH': 'age_years',
        'DAYS_EMPLOYED': 'employment_years',
        'NAME_INCOME_TYPE': 'income_type',
        'NAME_EDUCATION_TYPE': 'education',
        'EXT_SOURCE_2': 'ext_score_2',
        'EXT_SOURCE_3': 'ext_score_3',
        'TARGET': 'target',
    }

EMPLOYED_PLACEHOLDER = 365243   # kod "brak stażu" w DAYS_EMPLOYED
DAYS_PER_YEAR = 365.25




def load_data():
    """
    Wczytuje surowy plik CSV i zmienia nazwy kolumn
    Zwraca ramkę danych.
    """
    df = pd.read_csv(RAW_PATH, usecols=list(COLUMNS))
    df = df.rename(columns=COLUMNS)

    return df


def drop_wrong(df):
    """
    Usuwa wiersze, które nie mają sensu biznesowego
    """
    df = df.dropna(subset=['annuity'])
    return df

def convert_units(df):
    """
    Konwertuje jednostki na bardziej przyjazne dla człowieka
    """
    mask = df['employment_years'] != EMPLOYED_PLACEHOLDER
    df['employment_years'] = df['employment_years'].where(mask)
    df['employment_years'] = df['employment_years']/-DAYS_PER_YEAR
    df['age_years'] = df['age_years']/-DAYS_PER_YEAR
    df['term_months'] = df['credit_amount']/df['annuity']

    df = df.drop('annuity', axis=1)
    
    return df

def combine_categories(df):
    """
    Łączy rzadkie kategorie w jedną wspólną
    """
    categories_to_keep = ['Working', 'Commercial associate', 'Pensioner', 'State servant']
    
    mask = df['income_type'].isin(categories_to_keep)
    df['income_type'] = df['income_type'].where(mask, 'Other')

    return df


def save_data(df):
    """
    Zapisuje ramkę danych do pliku parquet
    """
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(OUTPUT_PATH, index=False)

def print_summary(df):
    """
    Wypisuje kontrolne statystyki gotowego zbioru.
    """
    print(f"Braki w employment_years: {df['employment_years'].isna().sum():,} (oczekiwane: 55,374)")
    print(f"Wiek: {df['age_years'].min():.1f}-{df['age_years'].max():.1f} lat")
    print(f"Liczba rat: {df['term_months'].min():.1f}-{df['term_months'].max():.1f} miesięcy")


def main():
    df = load_data()
    n_loaded = len(df)
    print(f"Wczytano: {n_loaded:,} wierszy")

    df = drop_wrong(df)
    print(f"Usunięto (brak raty): {n_loaded - len(df):,} wierszy")

    df = convert_units(df)
    df = combine_categories(df)
    print_summary(df)

    save_data(df)
    print(f"Zapisano: {len(df):,} wierszy -> {OUTPUT_PATH.name}")

if __name__ == "__main__":
    main()