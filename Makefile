.PHONY: all setup hooks install lint test
all: install lint test

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
	pipenv install --dev; \
	pipenv run pybabel compile --directory=translations; \
	pipenv run invenio collect; \
	pipenv run invenio webpack buildall; \

lint:
	# run the linter hooks from pre-commit on all files
	@ echo linting all files; \
	pre-commit run --all-files; \

test:
	# run the unit and integration test suites
	@ echo running all tests; \
	eval "$(pipenv run docker-services-cli up --db postgresql --search opensearch2 --cache redis --mq rabbitmq --env)"; \
	pipenv run python -m pytest -W ignore -s; \
	EXIT_CODE=$$?; \
	pipenv run docker-services-cli down; \
	exit $$EXIT_CODE; \
