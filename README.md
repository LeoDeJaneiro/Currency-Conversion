# Currency conversion

Modelling of a multi source - multi target concurrency conversion task.

The code has been formatted with `yapf`. For local development logs are stored in `./get_exchange_rates.log`

## Prerequisites

- Docker / Docker-Compose for local development using a PostgreSQL instance
- Python3 (tested with 3.9) & pipenv

## Prepare

- Install python3 dependencies

  ```bash
  pipenv install -r requirements.txt
  ```

- Rename `.env.sample` to `.env` and fill in info

## Run

```bash
# run PostgreSQL DB via Docker
docker-compose up -d
# run data load
pipenv run python3 src/main.py
```

## Tests

```bash
# run unit test
PYTHONPATH=. pipenv run pytest
```
