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
	mkdir -p .venv/var/instance/translations; \
	cp -r ./translations/. .venv/var/instance/translations/; \
	pipenv run python ./site/mex_invenio/scripts/merge_translations.py .venv/var/instance; \
	(cd site/mex_invenio && INVENIO_INSTANCE_PATH=../../.venv/var/instance npm install && INVENIO_INSTANCE_PATH=../../.venv/var/instance npm run convert-po); \
	pipenv run pybabel compile --directory=.venv/var/instance/translations; \
	pipenv run invenio collect; \
	pipenv run invenio webpack buildall; \

lint:
	# run the linter hooks from pre-commit on all files
	@ echo linting all files; \
	pre-commit run --all-files; \

test:
	# run the unit and integration test suites
	@ echo running all tests; \
	eval "$$(pipenv run docker-services-cli up --db postgresql --search opensearch2 --cache redis --mq rabbitmq --env 2>/dev/null)"; \
	pipenv run python -m pytest -W ignore -s; \
	EXIT_CODE=$$?; \
	pipenv run docker-services-cli down; \
	exit $$EXIT_CODE; \

# test one test file or one test: `make test_one TEST=<test_file_path>` or `make test_one TEST=<test_file_path>::<test_name>`
test_one:
	@echo "running single test: $(TEST)"; \
	PYTEST_ADDOPTS="-p no:coverage" \
	eval "$$(pipenv run docker-services-cli up --db postgresql --search opensearch2 --cache redis --mq rabbitmq --env)"; \
	trap 'pipenv run docker-services-cli down' EXIT; \
	pipenv run python -m pytest -W ignore -s $(TEST)
