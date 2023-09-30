.DEFAULT_GOAL := default

###### PACKAGE ACTIONS ######
reinstall_package:
	@pip uninstall -y stockprice || :
	@pip install -e

run_preprocess:
	python -c 'from stockprice.interface.main import preprocess; preprocess()'

run_train:
	python -c 'from stockprice.interface.main import train; train()'

run_pred:
	python -c 'from stockprice.interface.main import pred; pred()'

run_evaluate:
	python -c 'from stockprice.interface.main import evaluate; evaluate()'

run_all: run_preprocess run_train run_pred run_evaluate

# run_workflow:
# 	PREFECT__LOGGING__LEVEL=${PREFECT_LOG_LEVEL} python -m stockprice.interface.workflow

run_api:
	uvicorn stockprice.api.fast:app --reload

test_gcp_setup:
	@pytest \
	tests/all/test_gcp_setup.py::TestGcpSetup::test_setup_key_env \
	tests/all/test_gcp_setup.py::TestGcpSetup::test_setup_key_path \
	tests/all/test_gcp_setup.py::TestGcpSetup::test_code_get_project \
	tests/all/test_gcp_setup.py::TestGcpSetup::test_code_get_wagon_project

default:
	cat tests/api/test_output.txt

test_api_root:
	pytest \
	tests/api/test_endpoints.py::test_root_is_up --asyncio-mode=strict -W "ignore" \
	tests/api/test_endpoints.py::test_root_returns_greeting --asyncio-mode=strict -W "ignore"

test_api_predict:
	pytest \
	tests/api/test_endpoints.py::test_predict_is_up --asyncio-mode=strict -W "ignore" \
	tests/api/test_endpoints.py::test_predict_is_dict --asyncio-mode=strict -W "ignore" \
	tests/api/test_endpoints.py::test_predict_has_key --asyncio-mode=strict -W "ignore" \
	tests/api/test_endpoints.py::test_predict_val_is_float --asyncio-mode=strict -W "ignore"

test_api_on_prod:
	pytest \
	tests/api/test_cloud_endpoints.py --asyncio-mode=strict -W "ignore"

=
