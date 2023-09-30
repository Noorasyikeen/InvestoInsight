import pandas as pd
from prophet import Prophet
from sklearn.model_selection import train_test_split
from datetime import datetime
from math import sqrt
from sklearn.metrics import mean_squared_error
from sklearn.metrics import mean_absolute_error
import numpy as np
from prophet.diagnostics import cross_validation
from prophet.diagnostics import performance_metrics
from prophet.plot import add_changepoints_to_plot

def load_train_test (data):
    # Sort your DataFrame by the datetime column
    data = data.sort_values(by='ds')

    # Calculate the cut-off point for splitting
    cutoff_date = data['ds'].max() - pd.DateOffset(months=12)

    # Split the data into training and test sets
    train_data = data[data['ds'] <= cutoff_date]
    test_data = data[(data['ds'] > cutoff_date) & (data['ds'] <= cutoff_date + pd.DateOffset(months=12))]

    print("✅ Train Test Split")

    return train_data, test_data

def initialise_model_all(train_data, data):
#Runs a loop on all stocks and generates forecast for all.
    #Tickers
    tickers = data['Tickers'].unique()

    # Create an empty DataFrame to store all forecasts
    combined_forecasts = pd.DataFrame()

    # Loop through each unique 'ticker'
    for ticker in tickers:
        # Filter data for the current ticker
        stock_data = train_data[train_data['Tickers'] == ticker]

        # Initialize and fit the Prophet model
        model = Prophet(changepoint_prior_scale = 0.5,
                        seasonality_prior_scale = 0.1,
                        seasonality_mode = 'additive',
                        changepoint_range = 0.95)
        model.fit(stock_data)

        # Make predictions for the next 12 months
        future = model.make_future_dataframe(periods=12, freq='M')
        forecast = model.predict(future)

        # Add a column 'ticker' to the forecast DataFrame to indicate the stock ticker
        forecast['ticker'] = ticker

        # Concatenate the current forecast with the combined_forecasts DataFrame
        combined_forecasts = pd.concat([combined_forecasts, forecast])

    print("✅ Forecast Done")


    return combined_forecasts

def initialise_model_single(train_data, data, ticker):

    #Ticker data
    ticker_data = train_data.loc[train_data['Tickers'] == ticker]

    # Initialize and fit the Prophet model for the current ticker
    model = Prophet(changepoint_prior_scale = 0.5,
                    seasonality_prior_scale = 0.1,
                    seasonality_mode = 'additive',
                    changepoint_range = 0.95)
    model.fit(ticker_data)

    # Create a future DataFrame for predictions
    future = model.make_future_dataframe(periods=12, freq='M')  # Adjust as needed

    # Make predictions for the current ticker
    forecast = model.predict(future)

    #fig plot of prediction
    fig = model.plot(forecast)

    print("✅ Forecast Done")

    return forecast, fig
