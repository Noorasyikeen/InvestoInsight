import logging
import pandas as pd

from datetime import datetime, timedelta
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware

# from stockprice.ml_logic.preprocessor import preprocess_features
from stockprice.ml_logic.registry import load_model
from stockprice.ml_logic.data import get_stock_price
from stockprice.interface.main import pred
from stockprice.utils import get_last_day_of_month

def get_profit(end_price, start_price):
    profit = end_price - start_price
    return profit

def get_returns(end_price, start_price):
    returns = (end_price - start_price) / start_price * 100
    return returns

def get_chart_data(encoder_data):
    chart_data = encoder_data[['Date', 'stock_price']]
    return chart_data

def gen_date(start_date):
    date_range = [start_date + pd.DateOffset(months=i) for i in range(6)]
    formatted_dates = [date.strftime("%Y-%m") for date in date_range]
    return formatted_dates

# logging.basicConfig(
#     level=logging.INFO,
#     format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
#     datefmt="%Y-%m-%d %H:%M:%S",
#     filename="app.log",  # Specify the log file name
# )

# logger = logging.getLogger(__name__)

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
        input_date: str = Query(None, description="Stock buy-in date"), # 2013-07
        end_date: str = Query(None, description="Optional end date in %Y-%m format"),
        txn_price: float = Query(None, description="Price bought"),
        option: int = Query(..., description="Mandatory Processing option"),
    ):
    """
    Predict stock prices based on the provided ticker, input date, and processing option.
    Args:
        ticker (str): Stock ticker symbol (e.g., AAPL).
        input_date (str): Input date in "%Y-%m" format (e.g., 2023-08).
        option (int, optional): Processing option: 1, 2, or 3.
        end_date (str, optional): Optional end date in "%Y-%m" format.
        txn_price (float, optional): Optional price bought.
    Returns:
        dict: Response JSON based on the selected option.
    """
    # ticker = 'AAPL'
    # input_date = '2023-08'
    # end_date = '2023-12'
    # option = 1
    # txn_price = None
    # print(ticker, input_date, end_date, option)

    # locals() gets us all of our arguments back as a dictionary
    # https://docs.python.org/3/library/functions.html#locals
    input = pd.DataFrame(locals(), index=[0])

    input_date = get_last_day_of_month(input_date)
    end_date = get_last_day_of_month(end_date)

    model = app.state.model
    assert model is not None
    # print(model)
    start_date = pd.to_datetime("2023-10-31") # datetime.date.today()
    target_date = pd.to_datetime(end_date)
    formatted_dates = gen_date(start_date=start_date)

    # Calculate no. of months between the start and target date
    num_months = (target_date.year - start_date.year) * 12 + (target_date.month - start_date.month)
    target_idx = num_months

    input_date_price= get_stock_price(date=input_date, ticker=ticker)

    encoder_data, predictions, values_as_float = pred(ticker=ticker)
    prediction_data = {'Date': formatted_dates, 'stock_price': values_as_float}
    prediction_data = pd.DataFrame(prediction_data)
    # print(prediction_data)
    chart_data = get_chart_data(encoder_data=encoder_data)

    stock_prices = pd.concat([chart_data, prediction_data],
                             axis=0,
                             ignore_index=True)
    stock_prices['Date'] = pd.to_datetime(stock_prices['Date']).dt.strftime('%Y-%m')
    stock_prices = stock_prices.to_dict()
    # print(stock_prices)

    # Option 1: Expected Returns
    if option == 1:

        end_date_price = values_as_float[target_idx]

        if txn_price:
            expected_returns = get_returns(end_date_price, txn_price)
            profit = get_profit(end_date_price, txn_price)
        else:
            expected_returns = get_returns(end_date_price, input_date_price)
            profit = get_profit(end_date_price, input_date_price)

    elif option == 2:

        max_index = values_as_float.index(max(values_as_float))
        price_at_divestment = values_as_float[max_index]
        divestment_month = formatted_dates[max_index]

        if txn_price:
            profit = get_profit(price_at_divestment, txn_price)
            returns = get_returns(price_at_divestment, txn_price)
        else:
            profit = get_profit(price_at_divestment, input_date_price)
            returns = get_returns(price_at_divestment, input_date_price)
            # if price_at_divestment is not None and input_date_price is not None:
            #     profit = get_profit(price_at_divestment, input_date_price)
            #     returns = get_returns(price_at_divestment, input_date_price)

            # elif price_at_divestment is None:
            #     profit = get_profit(mean_price, input_date_price)
            #     returns = get_returns(mean_price, input_date_price)

            # elif input_date_price is None:
            #     profit = get_profit(price_at_divestment, mean_price)
            #     returns = get_returns(price_at_divestment, input_date_price)


    elif option == 3:

        max_index = values_as_float.index(max(values_as_float))
        min_index = values_as_float.index(min(values_as_float))
        max_price = values_as_float[max_index]
        min_price = values_as_float[min_index]
        returns = get_returns(max_price, min_price)
        profit = get_profit(max_price, min_price)
        holding_period = abs(max_index - min_index)

        # Calculate index differences
        index_diff = max_index - min_index
        sell_month = stock_prices['Date'][max_index]
        buy_month = stock_prices['Date'][min_index]

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
            'stock_prices': stock_prices,
        }

        return response_data
    elif option == 2:
        response_data = {
            'returns': returns,
            'profit': profit,
            'price_at_divestment': price_at_divestment,
            'divestment_month': divestment_month,
            'stock_prices': stock_prices,
        }
        return response_data
    elif option == 3:
        response_data = {
            'returns': returns,
            'profit': profit,
            'holding_period': holding_period,
            'stock_prices': stock_prices,
            'index_diff': index_diff,
            'sell_month': sell_month,
            'buy_month': buy_month,
        }
        return response_data

# @app.get("/")
# def root():
#     return dict(greeting="Hi there.")

# predict()
