import pandas as pd

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# from stockprice.ml_logic.preprocessor import preprocess_features
from stockprice.ml_logic.registry import load_model

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
        start_date: str,  # 2013-07-06
    ):      #
    """
    Assumes `start_date` is provided as a string by the user in "%Y-%m-%d" format
    """

    # locals() gets us all of our arguments back as a dictionary
    # https://docs.python.org/3/library/functions.html#locals
    X_pred = pd.DataFrame(locals(), index=[0])

    model = app.state.model
    assert model is not None

    # X_processed = preprocess_features(X_pred)
    y_pred = model.predict(X_pred)

    # ⚠️ fastapi only accepts simple Python data types as a return value
    # among them dict, list, str, int, float, bool
    # in order to be able to convert the api response to JSON

    # Calculate returns here
    return dict(fare_amount=float(y_pred))

@app.get("/")
def root():
    return dict(greeting="Hi there.")
