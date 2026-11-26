import argparse
import sqlite3
import sys
from contextlib import closing
from pathlib import Path


def quote_sqlite_identifier(name):
    return '"' + name.replace('"', '""') + '"'


def print_rows(cursor):
    column_names = [column[0] for column in cursor.description]
    found = False
    for row in cursor:
        print(dict(zip(column_names, row)))
        found = True

    if not found:
        print("Совпадений нет.")


def search_sqlite(args):
    database_uri = args.database.resolve().as_uri() + "?mode=ro"
    table = quote_sqlite_identifier(args.table)
    column = quote_sqlite_identifier(args.column)
    statement = (
        f"SELECT * FROM main.{table} AS source "
        f"WHERE instr(CAST(source.{column} AS TEXT), ?) > 0 LIMIT ?"
    )
    with closing(sqlite3.connect(database_uri, uri=True)) as connection:
        with closing(connection.execute(statement, (args.query, args.limit))) as cursor:
            print_rows(cursor)


def search_postgres(args):
    try:
        import psycopg
        from psycopg import sql
    except ImportError as error:
        raise RuntimeError(
            "Для PostgreSQL установите драйвер: python -m pip install -r requirements.txt"
        ) from error

    statement = sql.SQL(
        "SELECT * FROM {table} WHERE strpos(CAST({column} AS TEXT), %s) > 0 LIMIT %s"
    ).format(table=sql.Identifier(args.schema, args.table), column=sql.Identifier(args.column))

    try:
        with psycopg.connect() as connection:
            connection.read_only = True
            with connection.execute(statement, (args.query, args.limit)) as cursor:
                print_rows(cursor)
    except psycopg.Error as error:
        raise RuntimeError(str(error)) from error


def main():
    parser = argparse.ArgumentParser(description="Поиск по таблицам SQLite и PostgreSQL")
    commands = parser.add_subparsers(dest="backend", required=True)

    sqlite_parser = commands.add_parser("sqlite", help="поиск в файле SQLite")
    sqlite_parser.add_argument("database", type=Path, help="путь к существующему файлу базы")
    sqlite_parser.set_defaults(search=search_sqlite)

    postgres_parser = commands.add_parser("postgres", help="поиск в PostgreSQL")
    postgres_parser.add_argument("--schema", default="public", help="имя схемы (по умолчанию public)")
    postgres_parser.set_defaults(search=search_postgres)

    for command in (sqlite_parser, postgres_parser):
        command.add_argument("table", help="имя таблицы")
        command.add_argument("column", help="имя столбца")
        command.add_argument("query", help="искомый текст с учётом регистра")
        command.add_argument("--limit", type=int, default=100, help="максимум строк (по умолчанию 100)")

    args = parser.parse_args()
    if not args.query:
        parser.error("Укажите непустой текст для поиска.")
    if not 1 <= args.limit <= 2**63 - 1:
        parser.error("--limit должен быть положительным целым числом в диапазоне 64 бит.")

    try:
        args.search(args)
    except (OSError, sqlite3.Error, RuntimeError) as error:
        print(f"Ошибка поиска: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
