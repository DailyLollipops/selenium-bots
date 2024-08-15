# Selenium Bots

A collection of bots for selenium automation

## Setup

1. Install docker
2. Copy `.env.sample` and rename to `.env`
3. Fill out values for `.env` such as credentials etc.
4. Run docker compose with `docker compose up -d --remove-orphans`
5. Hub info can be view on `localhost:${HUB_PORT}`

## Running

Run container using:

```bash
docker compose up -d --remove-orphans
```

Running scripts are done inside the `runner`

```bash
docker compose exec runner bash
```

Once inside the runner:

```bash
python bots/{id}/handler.py
```

or run with params:

```bash
python bots/{id}/handler.py --params "{'key': 'value'}"
```

_Note: Params depends on bot_
