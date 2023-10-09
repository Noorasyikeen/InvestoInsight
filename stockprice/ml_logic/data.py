import io
import numpy as np
import pandas as pd

from google.cloud import storage
from colorama import Fore, Style
from pathlib import Path

from stockprice.params import *

def gcp_csv_to_df(bucket_name, gcs_dataset):
    """
    Read dataset from GCS bucket
    """
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(f"{gcs_dataset}.csv")
    data = blob.download_as_bytes()
    df = pd.read_csv(io.BytesIO(data))
    print(f'Pulled down file from bucket {bucket_name}, file name: {gcs_dataset}')

    return df

def df_to_gcp_csv(df, bucket_name, dest_file_name):
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(dest_file_name)
    blob.upload_from_string(df.to_csv(), 'text/csv')
    print(f'DataFrame uploaded to bucket {bucket_name}, file name: {dest_file_name}')

def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean raw data:
    1. Assign correct dtypes to each column
    2. Remove irrelevant columns
    """
    df = df.drop(columns=['Unnamed: 0'])
    df['Date'] = pd.to_datetime(df['Date'])

    print("✅ data cleaned")

    return df

def get_data_with_cache(
        bucket_name:str,
        gcs_dataset:str,
        cache_path:Path,
        data_has_header=True
    ) -> pd.DataFrame:
    """
    Retrieve `query` data from BigQuery, or from `cache_path` if the file exists
    Store at `cache_path` if retrieved from BigQuery for future use
    """
    if cache_path.is_file():
        print(Fore.BLUE + "\nLoad data from local CSV..." + Style.RESET_ALL)
        df = pd.read_csv(cache_path, header='infer' if data_has_header else None)
    else:
        print(Fore.BLUE + "\nLoad data from GCS bucket..." + Style.RESET_ALL)
        df = gcp_csv_to_df(bucket_name, gcs_dataset)

        # Store as CSV if the BQ query returned at least one valid line
        if df.shape[0] > 1:
            df.to_csv(cache_path, header=data_has_header, index=False)

    print(f"✅ Data loaded, with shape {df.shape}")

    return df

def get_stock_price(date, ticker):
    try:
        df = gcp_csv_to_df(bucket_name=BUCKET_NAME,
                           gcs_dataset=GCS_DATASET)
        price = df[(df['Date'] == date) & (df['Tickers'] == ticker)]['stock_price'].values[0]
        return price

    except IndexError:
        mean_price = df[df['Tickers'] == ticker]['stock_price'].mean()
        # return mean_price
        return None
