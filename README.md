# SQLite and PostgreSQL Search CLI

Search a specified table and column for a case-sensitive substring and print matching rows in the terminal.

## Features

- SQLite searches use a read-only file connection.
- PostgreSQL searches run in a read-only transaction using PostgreSQL connection settings.
- Both commands accept a row limit and treat the search string as a literal substring.

## Stack and architecture

`main.py` dispatches subcommands with `argparse`. SQLite uses the Python `sqlite3` module and the `instr` function. PostgreSQL uses Psycopg 3 and the `strpos` function. Search values are bound as query parameters. Table and column identifiers are quoted separately.

## Setup

Use Python 3.10 or later. For SQLite, run the script directly. For PostgreSQL, install the driver.

```sh
python -m pip install -r requirements.txt
```

## Configuration and examples

Search a local SQLite file.

```sh
python main.py sqlite ./data/sample.sqlite3 documents title "Safety" --limit 20
```

For PostgreSQL, configure the connection through libpq. A service entry and a password file can keep credentials out of command history. The example assumes that the `portfolio_demo` service already exists.

```powershell
$env:PGSERVICE = 'portfolio_demo'
python main.py postgres --schema public documents title "Safety" --limit 20
```

## Status and limitations

Each invocation searches one column and prints all fields of the selected rows. The default limit is 100 and row order is unspecified. Use test data when sharing a terminal transcript. The SQLite branch has a local smoke test against synthetic data. A live PostgreSQL connection has yet to be verified in this review.

## Кратко для портфолио

Консольная утилита для поиска подстрок в SQLite и PostgreSQL. Работает в режиме чтения, параметризует поисковые значения и ограничивает размер выдачи.
