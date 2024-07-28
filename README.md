# Selenium Bots

A collection of bots for selenium automation

## Setup

1. Install docker
2. Copy `.env.sample` and rename to `.env`
3. Fill out values for `.env` such as credentials etc.

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
