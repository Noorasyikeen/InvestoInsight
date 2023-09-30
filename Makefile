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
