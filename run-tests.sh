#!/bin/bash
source $(pipenv --venv)/bin/activate

eval "$(docker-services-cli up --db ${DB:-postgresql} --search ${SEARCH:-opensearch2} --cache ${CACHE:-redis} --mq ${MQ:-rabbitmq} --env)"

python -m pytest -W ignore -s

docker-services-cli down

deactivate
