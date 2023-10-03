import calendar
import pandas as pd

from datetime import datetime, timedelta
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware

# from stockprice.ml_logic.preprocessor import preprocess_features
from stockprice.ml_logic.registry import load_model
from stockprice.ml_logic.data import get_stock_price
from stockprice.interface.main import pred
from stockprice.utils import get_last_day_of_month
from stockprice.api.calc import profit, returns

app = FastAPI()

# Allowing all middleware is optional, but good practice for dev purposes
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

app.state.model = load_model()

@app.get("/predict")
def predict(
        ticker: str, # AAPL
        input_date: str,  # 2013-07
        end_date: str = Query(None, description="Optional end date in %Y-%m format"),
        txn_price: float = Query(None, description="Price bought"),
        option: int = Query(None, description="Processing option"),
    ):
    """
    Predict stock prices based on the provided ticker, input date, and processing option.
    Args:
        ticker (str): Stock ticker symbol (e.g., AAPL).
        input_date (str): Input date in "%Y-%m" format (e.g., 2023-08).
        option (int, optional): Processing option: 1, 2, or 3.
        end_date (str, optional): Optional end date in "%Y-%m" format.
        txn_price (floar, optional): Optional price bought.
    Returns:
        dict: Response JSON based on the selected option.
    """

    # locals() gets us all of our arguments back as a dictionary
    # https://docs.python.org/3/library/functions.html#locals
    X_pred = pd.DataFrame(locals(), index=[0])

    X_pred['input_date'] = get_last_day_of_month(input_date)
    X_pred['end_date'] = get_last_day_of_month(end_date)

    model = app.state.model
    assert model is not None

    start_date = pd.to_datetime("2023-09-30")
    target_date = pd.to_datetime(X_pred['end_date'])

    # Calculate no. of months between the start and target date
    num_months = (target_date.year - start_date.year) * 12 + (target_date.month - start_date.month)
    target_idx = num_months

    input_date_price = get_stock_price(date=X_pred['input_date'], ticker=ticker)

    if option == 1: # Expected returns
        predictions, values_as_float = pred(X_pred)
        end_date_price = values_as_float[target_idx]

        if txn_price:
            expected_returns = returns(end_date_price, txn_price)
            profit = profit(end_date_price, txn_price)
        else:
            expected_returns = returns(end_date_price, input_date_price)
            profit = profit(end_date_price, input_date_price)

    elif option == 2:
        predictions, values_as_float = pred(X_pred)
        max_index = values_as_float.index(max(values_as_float))
        # target_date = start_date + timedelta(days=target_idx * 30)
        price_at_divestment = values_as_float[max_index]

        if txn_price:
            profit = profit(price_at_divestment, txn_price)
            returns = returns(price_at_divestment, txn_price)
        else:
            profit = profit(price_at_divestment, input_date_price)
            returns = returns(price_at_divestment, input_date_price)

    elif option ==3:
        predictions, values_as_float = pred(X_pred)
        max_index = values_as_float.index(max(values_as_float))
        min_index = values_as_float.index(min(values_as_float))
        max_price = values_as_float[max_index]
        min_price = values_as_float[min_index]
        returns = max_price - min_price
        holding_period = abs(max_index - min_index)
    else:
        return {"error": "Invalid option. Please choose 1, 2, or 3."}

    # ⚠️ fastapi only accepts simple Python data types as a return value
    # among them dict, list, str, int, float, bool
    # in order to be able to convert the api response to JSON

    # Return response based on selected option
    if option == 1:
        response_data = {
            'expected_returns': expected_returns,
            'profit': profit,
        }
        return response_data
    elif option == 2:
        response_data = {
            'returns': returns,
            'profit': profit,
            'divestment_month': price_at_divestment, # should be date here, pending update
        }
        return response_data
    elif option == 3:
        response_data = {
            'returns': returns,
            'holding_period': holding_period,
        }
        return {"option": "C", "values": values_as_float}

@app.get("/")
def root():
    return dict(greeting="Hi there.")
