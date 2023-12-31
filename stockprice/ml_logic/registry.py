import glob
import os
import time
import pickle
import io
import torch
import pandas as pd

from colorama import Fore, Style
from google.cloud import storage

from stockprice.params import *

def save_results(params: dict, metrics: dict) -> None:

    timestamp = time.strftime("%Y%m%d-%H%M%S")

    # Check if the directory exists, and if not, create it
    if not os.path.exists(LOCAL_REGISTRY_PATH):
        os.makedirs(LOCAL_REGISTRY_PATH)

    # Save params locally
    if params is not None:
        params_path = os.path.join(LOCAL_REGISTRY_PATH, "params", timestamp + ".pickle")
        with open(params_path, "wb") as file:
            pickle.dump(params, file)

    # Save metrics locally
    if metrics is not None:
        metrics_path = os.path.join(LOCAL_REGISTRY_PATH, "metrics", timestamp + ".pickle")
        with open(metrics_path, "wb") as file:
            pickle.dump(metrics, file)

    print("✅ Results saved locally")


def save_model(model) -> None:
    """
    Persist trained model locally on the hard drive at f"{LOCAL_REGISTRY_PATH}/models/{timestamp}.h5"
    - if MODEL_TARGET='gcs', also persist it in your bucket on GCS at "models/{timestamp}.h5" --> unit 02 only
    - if MODEL_TARGET='mlflow', also persist it on MLflow instead of GCS (for unit 0703 only) --> unit 03 only
    """

    timestamp = time.strftime("%Y%m%d-%H%M%S")

    # Check if the directory exists, and if not, create it
    if not os.path.exists(LOCAL_REGISTRY_PATH):
        os.makedirs(LOCAL_REGISTRY_PATH)

    # Save model locally
    model_path = os.path.join(LOCAL_REGISTRY_PATH, "models", f"{timestamp}.pth")
    torch.save(model, model_path)

    print("✅ Model saved locally")

    if MODEL_TARGET == "gcs":

        model_filename = model_path.split("/")[-1] # e.g. "20230805-200538.pth" for instance
        client = storage.Client()
        bucket = client.bucket(BUCKET_NAME)
        blob = bucket.blob(f"models/{model_filename}")
        blob.upload_from_filename(model_path)

        print("✅ Model saved to GCS")

        return None

    return None


def load_model(stage="Production"):
    """
    Return a saved model:
    - locally (latest one in alphabetical order)
    - or from GCS (most recent one) if MODEL_TARGET=='gcs'  --> for unit 02 only
    - or from MLFLOW (by "stage") if MODEL_TARGET=='mlflow' --> for unit 03 only

    Return None (but do not Raise) if no model is found

    """

    # Check if the directory exists, and if not, create it
    if not os.path.exists(LOCAL_REGISTRY_PATH):
        os.makedirs(LOCAL_REGISTRY_PATH)

    if MODEL_TARGET == "local":
        print(Fore.BLUE + f"\nLoad latest model from local registry..." + Style.RESET_ALL)

        # Get the latest model version name by the timestamp on disk
        local_model_directory = os.path.join(LOCAL_REGISTRY_PATH, "models")
        local_model_paths = glob.glob(f"{local_model_directory}/*")

        if not local_model_paths:
            return None

        most_recent_model_path_on_disk = sorted(local_model_paths)[-1]

        print(Fore.BLUE + f"\nLoad latest model from disk..." + Style.RESET_ALL)

        latest_model = torch.load(most_recent_model_path_on_disk)

        print("✅ Model loaded from local disk")

        return latest_model

    elif MODEL_TARGET == "gcs":

        print(Fore.BLUE + f"\nLoad latest model from GCS..." + Style.RESET_ALL)

        client = storage.Client()
        blobs = list(client.get_bucket(BUCKET_NAME).list_blobs(prefix="models"))

        try:
            pth_blobs = [blob for blob in blobs if blob.name.endswith('.pth')]

            if not pth_blobs:
                print(f"\n❌ No .pth model found in GCS bucket")
                return None

            # Find the latest .pth model based on the 'updated' timestamp
            # latest_blob = max(pth_blobs, key=lambda x: x.updated)
            # client = storage.Client()
            # bucket = client.get_bucket(BUCKET_NAME)
            # blob = bucket.blob(latest_blob)
            # latest_model_path = "model/models_{latest_blob}.pth"
            # blob.download_to_filename(latest_model_path)
            model_path = "model/models_20231003-233216.pth"
            tft_model = torch.load(model_path)

            print("✅ Latest .pth model downloaded from cloud storage")

            return tft_model

        except Exception as e:
            print(f"\n❌ Error: {str(e)}")
            return None

    # elif MODEL_TARGET == "mlflow":
    #     print(Fore.BLUE + f"\nLoad [{stage}] model from MLflow..." + Style.RESET_ALL)

    #     # Load model from MLflow
    #     model = None
    #     mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
    #     client = MlflowClient()
    #     print(123)
    #     try:
    #         model_versions = client.get_latest_versions(name=MLFLOW_MODEL_NAME, stages=[stage])
    #         model_uri = model_versions[0].source

    #         assert model_uri is not None
    #     except:
    #         print(f"\n❌ No model found with name {MLFLOW_MODEL_NAME} in stage {stage}")

    #         return None

    #     model = torch.load(model_uri, map_location=torch.device("cpu"))

    #     print("✅ Model loaded from MLflow")
    #     return model
    else:
        return None



# def mlflow_transition_model(current_stage: str, new_stage: str) -> None:
#     """
#     Transition the latest model from the `current_stage` to the
#     `new_stage` and archive the existing model in `new_stage`
#     """
    # mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)

    # client = MlflowClient()

    # version = client.get_latest_versions(name=MLFLOW_MODEL_NAME, stages=[current_stage])

    # if not version:
    #     print(f"\n❌ No model found with name {MLFLOW_MODEL_NAME} in stage {current_stage}")
    #     return None

    # client.transition_model_version_stage(
    #     name=MLFLOW_MODEL_NAME,
    #     version=version[0].version,
    #     stage=new_stage,
    #     archive_existing_versions=True
    # )

    # print(f"✅ Model {MLFLOW_MODEL_NAME} (version {version[0].version}) transitioned from {current_stage} to {new_stage}")

    # return None


# def mlflow_run(func):
#     """
#     Generic function to log params and results to MLflow along with TensorFlow auto-logging

#     Args:
#         - func (function): Function you want to run within the MLflow run
#         - params (dict, optional): Params to add to the run in MLflow. Defaults to None.
#         - context (str, optional): Param describing the context of the run. Defaults to "Train".
#     """
#     def wrapper(*args, **kwargs):
#         mlflow.end_run()
#         mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
#         mlflow.set_experiment(experiment_name=MLFLOW_EXPERIMENT)

#         with mlflow.start_run():
#             mlflow.tensorflow.autolog()
#             results = func(*args, **kwargs)

#         print("✅ mlflow_run auto-log done")

#         return results
#     return wrapper
