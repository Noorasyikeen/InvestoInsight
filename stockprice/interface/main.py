import numpy as np
import pandas as pd

from pathlib import Path
from colorama import Fore, Style
from dateutil.parser import parse
from google.cloud import storage

from stockprice.params import *
from stockprice.ml_logic.data import get_data_with_cache, clean_data, df_to_gcp_csv
from stockprice.ml_logic.TFT_preprocessor import preprocessing
from stockprice.ml_logic.TFT_model import timeseries_instance, dataloader, optimal_learning_rate, initialize_model, train_model, evaluate_model
from stockprice.ml_logic.registry import load_model, save_model, save_results
# from stockprice.ml_logic.registry import mlflow_run, mlflow_transition_model

def preprocess() -> None:
    """
    - Get raw dataset from gcs bucket
    - Cache result
    """

    print(Fore.MAGENTA + "\n ⭐️ Use case: preprocess" + Style.RESET_ALL)

    # Retrieve data using `get_data_with_cache`
    data_query_cache_path = Path(LOCAL_DATA_PATH).joinpath("raw", f"{GCS_DATASET}.csv")
    data_query = get_data_with_cache(
        bucket_name = BUCKET_NAME,
        gcp_project=GCP_PROJECT,
        cache_path=data_query_cache_path,
        data_has_header=True
    )

    # Process data
    data_clean = clean_data(data_query)
    data = preprocessing(data_clean)

    df_to_gcp_csv(
        df=data,
        bucket_name=BUCKET_NAME,
        dest_file_name=f'processed_{GCS_DATASET}')

    print("✅ preprocess() done \n")

    return data

def train(data: pd.DataFrame = None) -> np.ndarray:

    # if df.shape[0] < 10:
    #     print("❌ Not enough processed data retrieved to train on")
    #     return None

    # Create TimeSeriesInstance
    training, validation = timeseries_instance(data)

    # Create dataloaders
    train_dataloader, val_dataloader = dataloader(training, validation)

    # Optimal learning rate
    learning_rate = optimal_learning_rate(training, train_dataloader, val_dataloader)

    trainer, tft = initialize_model(training, learning_rate)

    best_tft = train_model(trainer, tft, train_dataloader, val_dataloader)

    metrics = evaluate_model(best_tft, val_dataloader)

    params = dict(
        context="train",
        max_date=data.Date.max(),
        row_count=len(train_dataloader),
    )

    # Save results on the hard drive using stockprice.ml_logic.registry
    save_results(params=params, metrics=dict(metrics))

    # Save model weight on the hard drive (and optionally on GCS)
    save_model(model=best_tft)

    print("✅ train() done \n")

    return val_dataloader, metrics

def evaluate(
        val_dataloader,
        stage: str = "Production"
    ):
    """
    Evaluate the performance of the latest production model on processed data
    Return metrics
    """
    print(Fore.MAGENTA + "\n⭐️ Use case: evaluate" + Style.RESET_ALL)

    model = load_model(stage=stage)
    assert model is not None

    # Query your BigQuery processed table and get data_processed using `get_data_with_cache`
    # query = f"""
    #     SELECT * EXCEPT(_0)
    #     FROM {GCP_PROJECT}.{BQ_DATASET}.processed_{DATA_SIZE}
    # """

    # data_processed_cache_path = Path(f"{LOCAL_DATA_PATH}/processed/processed_{min_date}_{max_date}_{DATA_SIZE}.csv")
    # data_processed = get_data_with_cache(
    #     gcp_project=GCP_PROJECT,
    #     query=query,
    #     cache_path=data_processed_cache_path,
    #     data_has_header=False
    # )

    if val_dataloader.shape[0] == 0:
        print("❌ No data to evaluate on")
        return None

    metrics_dict = evaluate_model(model, val_dataloader)

    params = dict(
        context="evaluate", # Package behavior
        row_count=len(val_dataloader)
    )

    save_results(params=params, metrics=metrics_dict)

    print("✅ evaluate() done \n")

    return metrics_dict


def pred(X_pred: pd.DataFrame = None) -> np.ndarray:
    """
    Make a prediction using the latest trained model
    """

    print("\n⭐️ Use case: predict")

    # predict 6 months from current date
    max_prediction_length = 6

    if X_pred is None:
        X_pred = pd.DataFrame(dict(
        input_date=[pd.to_datetime("2023-07-31")],
        Ticker="AAPL"
    ))

    model = load_model()
    assert model is not None

    data = preprocess()

    start_date = pd.to_datetime("2018-01-31")
    target_date = pd.to_datetime(X_pred['input_date'])  # Replace with start date input from streamlit

    # Calculate no. of months between the start and target date
    num_months = (target_date.year - start_date.year) * 12 + (target_date.month - start_date.month)
    target_idx = num_months
    ticker = X_pred['Ticker']

    # select last 12 months from data (max_encoder_length is 12)
    encoder_data = data[lambda x: (x.Tickers == ticker) & (x.Index > x.Index.max() - 12)]

    # select last known data point and create decoder data from it by repeating it and incrementing the month
    last_data = data[lambda x: (x.Tickers == ticker) & (x.Index == x.Index.max())]
    decoder_data = pd.concat(
        [last_data.assign(date=lambda x: x.Date + pd.offsets.MonthBegin(i)) for i in range(1, max_prediction_length + 1)],
        ignore_index=True,
    )

    # add time index consistent with "data"
    decoder_data["Index"] = decoder_data["Date"].dt.year * 12 + decoder_data["Date"].dt.month
    decoder_data["Index"] += encoder_data["Index"].max() + 1 - decoder_data["Index"].min()

    # combine encoder and decoder data
    new_prediction_data = pd.concat([encoder_data, decoder_data], ignore_index=True)

    prediction = model.predict(
        encoder_data.filter(lambda x: (x.Tickers == ticker) & (x.time_idx_first_prediction == 15)),
        mode="quantiles",
        trainer_kwargs=dict(accelerator='cpu')
    )

    print("\n✅ prediction done: ", prediction, prediction.shape, "\n")
    return prediction


if __name__ == '__main__':
    preprocess()
    train()
    evaluate()
    pred()
