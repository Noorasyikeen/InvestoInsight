import os
import numpy as np

####### VARIABLES ######
MPS = os.environ["PYTORCH_ENABLE_MPS_FALLBACK"] = "1"
MODEL_TARGET = os.environ.get("MODEL_TARGET")
GCP_PROJECT = os.environ.get("GCP_PROJECT")
GCP_REGION = os.environ.get("GCP_REGION")
# BQ_DATASET = os.environ.get("BQ_DATASET")
# BQ_REGION = os.environ.get("BQ_REGION")
BUCKET_NAME = os.environ.get("BUCKET_NAME")
INSTANCE = os.environ.get("INSTANCE")
MLFLOW_TRACKING_URI = os.environ.get("MLFLOW_TRACKING_URI")
MLFLOW_EXPERIMENT = os.environ.get("MLFLOW_EXPERIMENT")
MLFLOW_MODEL_NAME = os.environ.get("MLFLOW_MODEL_NAME")
PREFECT_FLOW_NAME = os.environ.get("PREFECT_FLOW_NAME")
PREFECT_LOG_LEVEL = os.environ.get("PREFECT_LOG_LEVEL")
# EVALUATION_START_DATE = os.environ.get("EVALUATION_START_DATE")
GCR_IMAGE = os.environ.get("GCR_IMAGE")
GCR_REGION = os.environ.get("GCR_REGION")
GCR_MEMORY = os.environ.get("GCR_MEMORY")

##################  CONSTANTS  #####################
# LOCAL_DATA_PATH = os.path.join(os.path.expanduser('~'), ".lewagon", "mlops", "data")
# LOCAL_REGISTRY_PATH =  os.path.join(os.path.expanduser('~'), ".lewagon", "mlops", "training_outputs")

COLUMN_NAMES_RAW = ['Date', 'Dividend', 'Volume', 'stock_price',
       'fed_funds_rate', 'GDP', 'Tickers', 'debt_to_equity', 'EPS',
       'return_on_equity', 'quick ratio', 'operating_ratio',
       'inventory_turnover', 'pos_ma', 'neu_ma', 'neg_ma']

DTYPES_RAW = {
    'Date': "object",
    'Dividend': 'float64',
    'Volume': 'float64',
    'stock_price': 'float64',
    'fed_funds_rate': 'float64',
    'GDP': 'float64',
    'Tickers': 'object',
    'debt_to_equity': 'float64',
    'EPS': 'float64',
    'return_on_equity': 'float64',
    'quick ratio': 'float64',
    'operating_ratio': 'float64',
    'inventory_turnover': 'float64',
    'pos_ma': 'float64',
    'neu_ma': 'float64',
    'neg_ma': 'float64'
}

DTYPES_PROCESSED = {
    'Date': "dateime64[ns]",
    'Dividend': 'float64',
    'Volume': 'float64',
    'stock_price': 'float64',
    'fed_funds_rate': 'float64',
    'GDP': 'float64',
    'Tickers': 'object',
    'debt_to_equity': 'float64',
    'EPS': 'float64',
    'return_on_equity': 'float64',
    'quick ratio': 'float64',
    'operating_ratio': 'float64',
    'inventory_turnover': 'float64',
    'pos_ma': 'float64',
    'neu_ma': 'float64',
    'neg_ma': 'float64'
}




################## VALIDATIONS #################

env_valid_options = dict(
    # DATA_SIZE=["1k", "200k", "all"],
    MODEL_TARGET=["local", "gcs", "mlflow"],
)

def validate_env_value(env, valid_options):
    env_value = os.environ[env]
    if env_value not in valid_options:
        raise NameError(f"Invalid value for {env} in `.env` file: {env_value} must be in {valid_options}")


for env, valid_options in env_valid_options.items():
    validate_env_value(env, valid_options)
