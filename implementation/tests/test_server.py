# implementation/tests/test_server.py
import sqlite3
import pytest
from db import SQLiteAdapter, ValidationError

# ── shared test fixture ───────────────────────────────────────────────────────

MINI_SCHEMA = """
CREATE TABLE students (
    id     INTEGER PRIMARY KEY AUTOINCREMENT,
    name   TEXT    NOT NULL,
    email  TEXT    UNIQUE NOT NULL,
    cohort TEXT    NOT NULL,
    score  REAL    NOT NULL
);
CREATE TABLE courses (
    id    INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT    NOT NULL
);
"""

MINI_SEED = """
INSERT INTO students (name, email, cohort, score) VALUES
    ('Alice', 'alice@test.com', 'A1', 90),
    ('Bob',   'bob@test.com',   'A1', 80),
    ('Carol', 'carol@test.com', 'A2', 70);
INSERT INTO courses (title) VALUES ('Python'), ('SQL');
"""


@pytest.fixture
def adapter(tmp_path):
    db_path = str(tmp_path / "test.db")
    conn = sqlite3.connect(db_path)
    conn.executescript(MINI_SCHEMA)
    conn.executescript(MINI_SEED)
    conn.commit()
    conn.close()
    return SQLiteAdapter(db_path)


# ── core tests ────────────────────────────────────────────────────────────────

class TestCore:
    def test_list_tables(self, adapter):
        assert set(adapter.list_tables()) == {"students", "courses"}

    def test_get_table_schema(self, adapter):
        cols = adapter.get_table_schema("students")
        names = [c["name"] for c in cols]
        assert "id" in names
        assert "cohort" in names
        assert "score" in names

    def test_get_full_schema(self, adapter):
        schema = adapter.get_full_schema()
        assert "tables" in schema
        assert "students" in schema["tables"]
        assert "columns" in schema["tables"]["students"]

    def test_validate_table_unknown(self, adapter):
        with pytest.raises(ValidationError, match="Unknown table: 'xyz'"):
            adapter._validate_table("xyz")

    def test_validate_columns_unknown(self, adapter):
        with pytest.raises(ValidationError, match="Unknown column: 'bad_col'"):
            adapter._validate_columns("students", ["bad_col"])

    def test_validate_operator_unknown(self, adapter):
        with pytest.raises(ValidationError, match="Unsupported operator"):
            adapter._validate_operator("DROP")


# ── search tests ──────────────────────────────────────────────────────────────

class TestSearch:
    def test_search_all_rows(self, adapter):
        result = adapter.search("students")
        assert result["total"] == 3
        assert result["table"] == "students"
        assert len(result["rows"]) == 3

    def test_search_with_filter(self, adapter):
        result = adapter.search(
            "students",
            filters=[{"column": "cohort", "op": "=", "value": "A1"}],
        )
        assert result["total"] == 2
        assert all(r["cohort"] == "A1" for r in result["rows"])

    def test_search_with_column_selection(self, adapter):
        result = adapter.search("students", columns=["name", "cohort"])
        assert set(result["rows"][0].keys()) == {"name", "cohort"}

    def test_search_with_limit(self, adapter):
        result = adapter.search("students", limit=2)
        assert result["total"] == 2

    def test_search_with_offset(self, adapter):
        all_rows = adapter.search("students")["rows"]
        offset_rows = adapter.search("students", offset=1)["rows"]
        assert offset_rows[0]["id"] == all_rows[1]["id"]

    def test_search_order_descending(self, adapter):
        result = adapter.search("students", order_by="score", descending=True)
        scores = [r["score"] for r in result["rows"]]
        assert scores == sorted(scores, reverse=True)

    def test_search_unknown_table(self, adapter):
        with pytest.raises(ValidationError, match="Unknown table"):
            adapter.search("unicorns")

    def test_search_unknown_column_in_filter(self, adapter):
        with pytest.raises(ValidationError, match="Unknown column"):
            adapter.search(
                "students",
                filters=[{"column": "bad_col", "op": "=", "value": "x"}],
            )

    def test_search_bad_operator(self, adapter):
        with pytest.raises(ValidationError, match="Unsupported operator"):
            adapter.search(
                "students",
                filters=[{"column": "cohort", "op": "INJECT", "value": "x"}],
            )


# ── insert tests ──────────────────────────────────────────────────────────────

class TestInsert:
    def test_insert_valid(self, adapter):
        result = adapter.insert("students", {
            "name": "Dave", "email": "dave@test.com",
            "cohort": "B1", "score": 75.0,
        })
        assert result["id"] is not None
        assert result["inserted"]["name"] == "Dave"

    def test_insert_persists(self, adapter):
        adapter.insert("students", {
            "name": "Eve", "email": "eve@test.com",
            "cohort": "B1", "score": 68.0,
        })
        found = adapter.search(
            "students",
            filters=[{"column": "email", "op": "=", "value": "eve@test.com"}],
        )
        assert found["total"] == 1

    def test_insert_empty_values(self, adapter):
        with pytest.raises(ValidationError, match="cannot be empty"):
            adapter.insert("students", {})

    def test_insert_unknown_table(self, adapter):
        with pytest.raises(ValidationError, match="Unknown table"):
            adapter.insert("ghosts", {"name": "Ghost"})

    def test_insert_unknown_column(self, adapter):
        with pytest.raises(ValidationError, match="Unknown column"):
            adapter.insert("students", {"bad_col": "x"})


# ── aggregate tests ───────────────────────────────────────────────────────────

class TestAggregate:
    def test_count(self, adapter):
        result = adapter.aggregate("students", "count")
        assert result["rows"][0]["value"] == 3

    def test_avg(self, adapter):
        result = adapter.aggregate("students", "avg", column="score")
        assert abs(result["rows"][0]["value"] - 80.0) < 0.01

    def test_sum(self, adapter):
        result = adapter.aggregate("students", "sum", column="score")
        assert result["rows"][0]["value"] == 240

    def test_min(self, adapter):
        result = adapter.aggregate("students", "min", column="score")
        assert result["rows"][0]["value"] == 70

    def test_max(self, adapter):
        result = adapter.aggregate("students", "max", column="score")
        assert result["rows"][0]["value"] == 90

    def test_count_group_by(self, adapter):
        result = adapter.aggregate("students", "count", group_by="cohort")
        groups = {r["grp"]: r["value"] for r in result["rows"]}
        assert groups["A1"] == 2
        assert groups["A2"] == 1

    def test_avg_group_by(self, adapter):
        result = adapter.aggregate(
            "students", "avg", column="score", group_by="cohort"
        )
        groups = {r["grp"]: r["value"] for r in result["rows"]}
        assert groups["A1"] == 85.0
        assert groups["A2"] == 70.0

    def test_count_with_filter(self, adapter):
        result = adapter.aggregate(
            "students", "count",
            filters=[{"column": "cohort", "op": "=", "value": "A1"}],
        )
        assert result["rows"][0]["value"] == 2

    def test_bad_metric(self, adapter):
        with pytest.raises(ValidationError, match="Unsupported metric"):
            adapter.aggregate("students", "drop_table")

    def test_avg_missing_column(self, adapter):
        with pytest.raises(ValidationError, match="requires a column"):
            adapter.aggregate("students", "avg")

    def test_unknown_table(self, adapter):
        with pytest.raises(ValidationError, match="Unknown table"):
            adapter.aggregate("unicorns", "count")
