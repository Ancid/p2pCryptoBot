.PHONY: help docs
.DEFAULT_GOAL := help

help:
	@fgrep -h "##" $(MAKEFILE_LIST) | fgrep -v fgrep | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

lint: ## Run code linters
	black --check app
	isort --check app
	flake8 app
	mypy app

fmt format: ## Run code formatters
	isort app
	black app

run-dev:  ## Run dev servce
	uvicorn app.main:app --port 5000 --reload