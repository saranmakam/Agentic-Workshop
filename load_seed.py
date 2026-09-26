"""Load seed tickets and customers into the local SQLite database."""

from __future__ import annotations

import csv
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DB_PATH = ROOT / "app.db"
SEED_DIR = ROOT / "seed"

TICKETS_COLUMNS = ("ticket_id", "customer_id", "created_at", "text")
CUSTOMERS_COLUMNS = ("customer_id", "name", "plan", "open_tickets")


def _load_csv(path: Path, expected_columns: tuple[str, ...]) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            raise ValueError(f"{path.name} has no header row")
        actual = tuple(reader.fieldnames)
        if actual != expected_columns:
            raise ValueError(
                f"{path.name} columns must be {list(expected_columns)}; got {list(actual)}"
            )
        return list(reader)


def load_seed(db_path: Path | None = None, seed_dir: Path | None = None) -> None:
    """Replace tickets and customers in db_path with the contents of the seed CSVs."""
    db_path = DB_PATH if db_path is None else db_path
    seed_dir = SEED_DIR if seed_dir is None else seed_dir
    tickets = _load_csv(seed_dir / "tickets.csv", TICKETS_COLUMNS)
    customers = _load_csv(seed_dir / "customers.csv", CUSTOMERS_COLUMNS)

    with sqlite3.connect(db_path) as conn:
        conn.execute("DROP TABLE IF EXISTS tickets")
        conn.execute("DROP TABLE IF EXISTS customers")
        conn.execute(
            """
            CREATE TABLE tickets (
                ticket_id TEXT PRIMARY KEY,
                customer_id TEXT NOT NULL,
                created_at TEXT NOT NULL,
                text TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE customers (
                customer_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                plan TEXT NOT NULL,
                open_tickets INTEGER NOT NULL
            )
            """
        )
        conn.executemany(
            "INSERT INTO tickets (ticket_id, customer_id, created_at, text) VALUES (?, ?, ?, ?)",
            [
                (row["ticket_id"], row["customer_id"], row["created_at"], row["text"])
                for row in tickets
            ],
        )
        conn.executemany(
            "INSERT INTO customers (customer_id, name, plan, open_tickets) VALUES (?, ?, ?, ?)",
            [
                (row["customer_id"], row["name"], row["plan"], int(row["open_tickets"]))
                for row in customers
            ],
        )
        conn.commit()


def main() -> None:
    load_seed()


if __name__ == "__main__":
    main()
