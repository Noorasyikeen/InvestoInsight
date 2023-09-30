import numpy as np
import pandas as pd

def preprocessing(raw_data):
    data = raw_data.copy()
    data['Date'] = pd.to_datetime(data['Date'])
    data['time_idx'] = data.groupby('Tickers').cumcount()

    print("✅ Preprocessing")

    return data
