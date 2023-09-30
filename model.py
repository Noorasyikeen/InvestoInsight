from pathlib import Path
import lightning.pytorch as pl
from lightning.pytorch.callbacks import EarlyStopping, LearningRateMonitor
from lightning.pytorch.loggers import TensorBoardLogger
import numpy as np
import pandas as pd
from pytorch_forecasting import Baseline, TemporalFusionTransformer, TimeSeriesDataSet
from pytorch_forecasting.metrics import MAE, SMAPE, RMSE, PoissonLoss, QuantileLoss
from pytorch_forecasting.models.temporal_fusion_transformer.tuning import optimize_hyperparameters
from pytorch_forecasting.data import GroupNormalizer

# def load_pretrained_model(model_path):
#     model = joblib.load(model_path)
#     return model

# Load the pretrained model once when the script is run
best_model_path = '/Users/zoeyneo/code/zoeyneo/investoinsight/streamlit_app/epoch=7-step=3104.ckpt'
best_tft = TemporalFusionTransformer.load_from_checkpoint(best_model_path)

def load_pretrained_model():
    return best_tft

def make_predictions(best_tft):
    # if __name__ == '__main__':
        st_ticker = 'AAPL'
        df = pd.read_csv('/Users/zoeyneo/code/zoeyneo/investoinsight/streamlit_app/sorted_feature_matrix.csv')
        df.drop(columns=['Unnamed: 0'], inplace=True)

        df_pytorch = df.copy()
        df_pytorch['Date'] = pd.to_datetime(df['Date'])
        df_pytorch['Index'] = df_pytorch.groupby('Tickers').cumcount()
        # select last 6 months from data (max_encoder_length is 6)
        encoder_data = df_pytorch[lambda x: (x.Tickers == st_ticker) & (x.Index > x.Index.max() - 12)]
        # select last known data point and create decoder data from it by repeating it and incrementing the month
        last_data = df_pytorch[lambda x: (x.Tickers == st_ticker) & (x.Index == x.Index.max())]
        decoder_data = pd.concat(
            [last_data.assign(date=lambda x: x.Date + pd.offsets.MonthBegin(i)) for i in range(1, 12 + 1)],
            ignore_index=True,
        )
        # add time index consistent with "data"
        decoder_data["Index"] = decoder_data["Date"].dt.year * 12 + decoder_data["Date"].dt.month
        decoder_data["Index"] += encoder_data["Index"].max() + 1 - decoder_data["Index"].min()
        # adjust additional time feature(s)
        # decoder_data["month"] = decoder_data.date.dt.month.astype(str).astype("category")  # categories have be strings
        # combine encoder and decoder data
        new_prediction_data = pd.concat([encoder_data, decoder_data], ignore_index=True)

        # new_raw_predictions = best_tft.predict(
        #     encoder_data(lambda x: (x.Tickers == st_ticker) & (x.time_idx_first_prediction == 15)),
        #     mode="raw",
        #     return_x=True,
        #     trainer_kwargs=dict(accelerator='cpu')
        # )

        new_raw_predictions = best_tft.predict(encoder_data,
                                            mode="raw",
                                            return_x=True,
                                            trainer_kwargs=dict(accelerator='cpu'))

        prediction_fig = best_tft.plot_prediction(new_raw_predictions.x, new_raw_predictions.output,
                                idx=0, show_future_observed=True)

        # Feature prioritization
        interpretation = best_tft.interpret_output(new_raw_predictions.output, reduction='sum') #ZN: changed to new_raw_predictions.output, pls check
        intepretation_fig = best_tft.plot_interpretation(interpretation)

        prediction_length=6
        train_split = df_pytorch["Index"].max() - prediction_length * 2
        training = TimeSeriesDataSet(
        df_pytorch[lambda x:x.Index <= train_split],
        group_ids=['Tickers'],
        target='stock_price',
        time_idx='Index',
        max_encoder_length=6,
        max_prediction_length=12,
        static_categoricals=['Tickers'],
        time_varying_known_reals=["Date", "Dividend", 'Volume', 'fed_funds_rate', 'GDP',
                                'debt_to_equity', 'EPS', 'return_on_equity', 'quick ratio',
                                'operating_ratio', 'inventory_turnover'],
        # time_varying_unknown_categoricals=[],
        time_varying_unknown_reals=["stock_price", 'pos_ma','neu_ma', 'neg_ma'],
        target_normalizer=GroupNormalizer(
            groups=['Tickers'], transformation="softplus"
        ),
        add_relative_time_idx=True,
        add_target_scales=True,
        add_encoder_length=True)
        # Create validation set
        # (predict=True) to predict last max_prediction_length points in time for each series
        validation = TimeSeriesDataSet.from_dataset(training, df_pytorch, predict=True, stop_randomization=True)
        # Create dataloaders
        batch_size=64
        # train_dataloader = training.to_dataloader(train=True, batch_size=batch_size, num_workers=0)
        val_dataloader = validation.to_dataloader(train=False, batch_size=batch_size * 10, num_workers=0)

        # calculate mean absolute error on validation set
        predictions = best_tft.predict(val_dataloader, return_y=True, trainer_kwargs=dict(accelerator="cpu"))
        mae_score = MAE()(predictions.output, predictions.y)
        smape_score = SMAPE()(predictions.output, predictions.y)
        return [prediction_fig, intepretation_fig, mae_score, smape_score]
