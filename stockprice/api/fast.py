import calendar
import pandas as pd

from datetime import datetime
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# from stockprice.ml_logic.preprocessor import preprocess_features
from stockprice.ml_logic.registry import load_model
from stockprice.interface.main import pred

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
    ):      #
    """
    Assumes `start_date` is provided as a string by the user in "%Y-%m-%d" format
    """

    # locals() gets us all of our arguments back as a dictionary
    # https://docs.python.org/3/library/functions.html#locals
    X_pred = pd.DataFrame(locals(), index=[0])

    # Parse the input date
    month, year = map(int, input_date.split('/'))
    last_day = calendar.monthrange(year, month)[1]
    last_day_date = datetime(year, month, last_day)

    X_pred['input_date'] = last_day_date.strftime("%Y-%m-%d")

    model = app.state.model
    assert model is not None

    # X_processed = preprocess_features(X_pred)
    predictions = pred(X_pred)

    # ⚠️ fastapi only accepts simple Python data types as a return value
    # among them dict, list, str, int, float, bool
    # in order to be able to convert the api response to JSON

    # Calculate returns here
    return dict(stockprice=float(predictions))

@app.get("/")
def root():
    return dict(greeting="Hi there.")
