"""Tests for the Epic 1 seed loader."""

import sqlite3
from pathlib import Path

from load_seed import CUSTOMERS_COLUMNS, TICKETS_COLUMNS, load_seed

ROOT = Path(__file__).resolve().parent.parent
SEED = ROOT / "seed"


def _table_rows(conn: sqlite3.Connection, table: str) -> list[tuple]:
    return list(conn.execute(f"SELECT * FROM {table} ORDER BY 1"))


def _columns(conn: sqlite3.Connection, table: str) -> list[str]:
    return [row[1] for row in conn.execute(f"PRAGMA table_info({table})")]


def test_load_seed_creates_expected_tables_and_columns(tmp_path: Path) -> None:
    db_path = tmp_path / "app.db"
    load_seed(db_path=db_path, seed_dir=SEED)

    with sqlite3.connect(db_path) as conn:
        assert _columns(conn, "tickets") == list(TICKETS_COLUMNS)
        assert _columns(conn, "customers") == list(CUSTOMERS_COLUMNS)
        assert conn.execute("SELECT COUNT(*) FROM tickets").fetchone()[0] == 24
        assert conn.execute("SELECT COUNT(*) FROM customers").fetchone()[0] == 20


def test_load_seed_is_idempotent(tmp_path: Path) -> None:
    db_path = tmp_path / "app.db"
    load_seed(db_path=db_path, seed_dir=SEED)
    with sqlite3.connect(db_path) as conn:
        first_tickets = _table_rows(conn, "tickets")
        first_customers = _table_rows(conn, "customers")

    load_seed(db_path=db_path, seed_dir=SEED)
    with sqlite3.connect(db_path) as conn:
        assert _table_rows(conn, "tickets") == first_tickets
        assert _table_rows(conn, "customers") == first_customers


def test_load_seed_does_not_modify_seed_files(tmp_path: Path) -> None:
    tickets_before = (SEED / "tickets.csv").read_bytes()
    customers_before = (SEED / "customers.csv").read_bytes()
    load_seed(db_path=tmp_path / "app.db", seed_dir=SEED)
    assert (SEED / "tickets.csv").read_bytes() == tickets_before
    assert (SEED / "customers.csv").read_bytes() == customers_before


def test_load_seed_matches_mcp_query_shape(tmp_path: Path) -> None:
    db_path = tmp_path / "app.db"
    load_seed(db_path=db_path, seed_dir=SEED)
    with sqlite3.connect(db_path) as conn:
        conn.row_factory = sqlite3.Row
        ticket = dict(
            conn.execute(
                "SELECT ticket_id, customer_id, created_at, text FROM tickets WHERE ticket_id = ?",
                ("T-1042",),
            ).fetchone()
        )
        customer = dict(
            conn.execute(
                "SELECT customer_id, name, plan, open_tickets FROM customers WHERE customer_id = ?",
                ("C-77",),
            ).fetchone()
        )
    assert ticket["customer_id"] == "C-77"
    assert "charged twice" in ticket["text"]
    assert customer["plan"] == "Enterprise"
    assert isinstance(customer["open_tickets"], int)
