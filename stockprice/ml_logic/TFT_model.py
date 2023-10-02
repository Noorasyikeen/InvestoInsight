import copy
import pickle
from pathlib import Path
import warnings

import lightning.pytorch as pl
from lightning.pytorch.callbacks import EarlyStopping, LearningRateMonitor, ModelCheckpoint
from lightning.pytorch.loggers import TensorBoardLogger
from lightning.pytorch.tuner import Tuner
import numpy as np
import pandas as pd
import torch
import math

from pytorch_forecasting import Baseline, TemporalFusionTransformer, TimeSeriesDataSet
from pytorch_forecasting.data import GroupNormalizer
from pytorch_forecasting.metrics import MAE, SMAPE, RMSE, PoissonLoss, QuantileLoss
from pytorch_forecasting.models.temporal_fusion_transformer.tuning import optimize_hyperparameters

def timeseries_instance(data):
    """
    Create multivariate timeseries instance
    """
    prediction_length=6
    train_split = data["time_idx"].max() - prediction_length

    training = TimeSeriesDataSet(
        data[lambda x:x.time_idx <= train_split],
        group_ids=['Tickers'],
        target='stock_price',
        time_idx='time_idx',
        max_encoder_length=6,
        max_prediction_length=6,
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
        add_encoder_length=True
        )

    validation = TimeSeriesDataSet.from_dataset(
        training,
        data,
        predict=True,
        stop_randomization=True
        )

    print("✅ Timeseries instance created")

    return training, validation

def dataloader(training, validation, batch_size=64):
    train_dataloader = training.to_dataloader(
        train=True,
        batch_size=batch_size,
        num_workers=0
        )
    val_dataloader = validation.to_dataloader(
        train=False,
        batch_size=batch_size,
        num_workers=0
        )

    print("✅ Dataloaders created")

    return train_dataloader, val_dataloader

def optimal_learning_rate(training, train_dataloader, val_dataloader):
    # configure network and trainer
    pl.seed_everything(42)
    trainer = pl.Trainer(
        accelerator="cpu",
        # clipping gradients is a hyperparameter and important to prevent divergance
        # of the gradient for recurrent neural networks
        gradient_clip_val=0.1,
    )


    tft = TemporalFusionTransformer.from_dataset(
        training,
        # not meaningful for finding the learning rate but otherwise very important
        learning_rate=0.03,
        hidden_size=160,
        # most important hyperparameter apart from learning rate
        # number of attention heads. Set to up to 4 for large datasets
        attention_head_size=4,
        dropout=0.1,  # between 0.1 and 0.3 are good values
        hidden_continuous_size=160,  # set to <= hidden_size
        loss=QuantileLoss(),
        optimizer="Ranger"
        # reduce learning rate if no improvement in validation loss after x epochs
        # reduce_on_plateau_patience=1000,
    )

    res = Tuner(trainer).lr_find(
    tft,
    train_dataloaders=train_dataloader,
    val_dataloaders=val_dataloader,
    max_lr=10.0,
    min_lr=1e-6,
    )

    learning_rate = res.suggestion()

    print(f"✅ Optimal learning rate: {learning_rate}")

    return learning_rate

def initialize_model(training, learning_rate):
    early_stop_callback = EarlyStopping(monitor='val_loss',
                                    min_delta=1e-4,
                                    patience=5,
                                    verbose=True,
                                    mode='min')
    checkpoint_callback = ModelCheckpoint(save_top_k=1,
                                          monitor='val_loss',
                                          mode='min')
    # log the learning rate
    lr_logger = LearningRateMonitor()

    # logging results to tensorboard
    logger = TensorBoardLogger('lightning_logs')

    trainer = pl.Trainer(
        max_epochs=50,
        accelerator='cpu',
        devices=1,
        enable_model_summary=True,
        gradient_clip_val=0.1,
        # fast_dev_run=True # for checking that networkor dataset has no serious bugs
        callbacks=[lr_logger, early_stop_callback, checkpoint_callback],
        enable_checkpointing=True,
        logger=logger
        )

    tft = TemporalFusionTransformer.from_dataset(
        training,
        learning_rate=0.003, # learning_rate + 0.0005,
        hidden_size=160,
        attention_head_size=4,
        dropout=0.1,
        hidden_continuous_size=160,
        output_size=7,
        loss=QuantileLoss(),
        optimizer='Ranger',
        log_interval=10, # logging every 10 batches
        reduce_on_plateau_patience=4
        )

    print("✅ Model initialized")

    return trainer, tft

def train_model(trainer, tft, train_dataloader, val_dataloader):
    trainer.fit(
        tft,
        train_dataloaders=train_dataloader,
        val_dataloaders=val_dataloader
        )
    best_model_path = trainer.checkpoint_callback.best_model_path
    best_model_score = trainer.checkpoint_callback.best_model_score
    # print(best_model_path)
    best_tft = TemporalFusionTransformer.load_from_checkpoint(best_model_path)

    print("✅ Model trained")

    return best_tft

def evaluate_model(best_tft, val_dataloader):
    predictions = best_tft.predict(val_dataloader, return_y=True, trainer_kwargs=dict(accelerator="cpu"))
    SMAPE = SMAPE()(predictions.output, predictions.y)
    MAE = MAE()(predictions.output, predictions.y)
    RMSE = RMSE()(predictions.output, predictions.y)

    metrics = {
        "SMAPE": SMAPE,
        "MAE": MAE,
        "RMSE": RMSE
    }

    print(f"✅ Model evaluated,")
    print(f"SMAPE: {round(SMAPE, 2)}")
    print(f"MAE: {round(MAE, 2)}")
    print(f"RMSE: {round(RMSE, 2)}")

    return metrics

def hyperparameter_tuning(train_dataloader, val_dataloader):
    study = optimize_hyperparameters(
        train_dataloader,
        val_dataloader,
        model_path='optuna_test',
        n_trials=200,
        max_epochs=50,
        gradient_clip_val_range=(0.01, 1.0),
        hidden_size_range=(8, 240),
        hidden_continuous_size_range=(8, 240),
        attention_head_size_range=(1, 4),
        learning_rate_range=(0.001, 0.1),
        dropout_range=(0.1, 0.3),
        trainer_kwargs=dict(accelerator='cpu',limit_train_batches=30),
        reduce_on_plateau_patience=4,
        use_learning_rate_finder=False # use Optuna to find ideal learning rate or use in-built learning rate finder
    )

    # save results
    with open("test_study.pkl", "wb") as fout:
        pickle.dump(study, fout)

    # show best hyperparameters
    best_hyperparameters = (study.best_trial_params)

    return best_hyperparameters
