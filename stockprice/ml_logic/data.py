import numpy as np
import pandas as pd

def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean raw data:
    1. Assign correct dtypes to each column
    2. Remove irrelevant records
    """
    df = df.drop_duplicates()
    df = df.dropna(how='any', axis=0)

    return df
