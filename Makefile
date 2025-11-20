.PHONY: all setup hooks install lint test
all: install lint

setup:
	# install meta requirements system-wide
	@ echo installing requirements; \
	pip --disable-pip-version-check install --force-reinstall -r requirements.txt; \

hooks:
	# install pre-commit hooks when not in CI
	@ if [ -z "$$CI" ]; then \
		pre-commit install; \
	fi; \

install: setup hooks
	# install packages from lock file in local virtual environment
	@ echo installing package; \
	pipenv install --verbose --dev; \
	pipenv run pybabel compile --directory=translations; \
	pipenv run invenio collect --verbose; \
	pipenv run invenio webpack buildall; \
	pipenv run invenio webpack install; \

lint:
	# run the linter hooks from pre-commit on all files
	@ echo linting all files; \
	pre-commit run --all-files; \

test:
	# run the unit and integration test suites
	@ echo running all tests; \
	pipenv run docker-services-cli up --db postgresql --search opensearch2 --cache redis --mq rabbitmq; \
	eval "$(pipenv run docker-services-cli up --db postgresql --search opensearch2 --cache redis --mq rabbitmq --env)"; \
	pipenv run python -m pytest -W ignore -s; \
	EXIT_CODE=$$?; \
	pipenv run docker-services-cli down; \
	exit $$EXIT_CODE; \
