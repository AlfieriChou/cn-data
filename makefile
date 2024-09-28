#############################
ENV_FILE ?= .env

check:
	ruff check --fix

format:
	ruff format --config indent-width=2

install:
	pip3 install -r requirements.txt

initialize:
	python3 -m pipreqs.pipreqs --encoding=utf8 --force
