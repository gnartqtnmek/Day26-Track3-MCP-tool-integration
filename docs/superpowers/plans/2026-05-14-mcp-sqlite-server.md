# FastMCP SQLite Lab — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a production-ready MCP server using FastMCP + SQLite exposing `search`, `insert`, and `aggregate` tools with schema resources, safe validation, and demo materials — targeting 100/100 on the lab rubric.

**Architecture:** `SQLiteAdapter` in `db.py` owns all DB logic and validation; `mcp_server.py` imports the adapter and wires it to FastMCP tools/resources. `init_db.py` creates `lab.db` with schema + seed data. `verify_server.py` tests the adapter directly (no MCP protocol needed) for quick CLI verification.

**Tech Stack:** Python 3.10+, fastmcp ≥ 2.0, pytest ≥ 8.0, sqlite3 (stdlib)

---

## File Map

| File | Responsibility |
|------|---------------|
| `implementation/db.py` | `ValidationError`, `SQLiteAdapter` (connect, validate, search, insert, aggregate, schema) |
| `implementation/init_db.py` | Schema SQL, seed SQL, `create_database()` |
| `implementation/mcp_server.py` | FastMCP tools + resources, argparse transport flag |
| `implementation/verify_server.py` | Manual CLI verification script (imports adapter directly) |
| `implementation/tests/test_server.py` | pytest: TestCore, TestSearch, TestInsert, TestAggregate |
| `implementation/requirements.txt` | fastmcp, pytest |

---

## Task 1: Project Setup

**Files:**
- Create: `implementation/requirements.txt`
- Create: `implementation/tests/__init__.py`

- [ ] **Step 1: Create directories**

```bash
mkdir -p implementation/tests
```

- [ ] **Step 2: Create `implementation/requirements.txt`**

```
fastmcp>=2.0
pytest>=8.0
```

- [ ] **Step 3: Create virtual environment and install**

```bash
cd implementation
python -m venv .venv

# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

pip install -r requirements.txt
```

Expected: `Successfully installed fastmcp-X.X.X pytest-X.X.X ...`

- [ ] **Step 4: Create empty `tests/__init__.py`**

```python
```

(empty file — needed so pytest can discover the package)

- [ ] **Step 5: Verify fastmcp is importable**

```bash
python -c "import fastmcp; print(fastmcp.__version__)"
```

Expected: prints a version string like `2.x.x`

- [ ] **Step 6: Commit**

```bash
git add implementation/requirements.txt implementation/tests/__init__.py
git commit -m "chore: set up implementation project structure"
```

---

## Task 2: Database Initialization (`init_db.py`)

**Files:**
- Create: `implementation/init_db.py`

- [ ] **Step 1: Write `init_db.py`**

```python
# implementation/init_db.py
import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "lab.db")

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS students (
    id     INTEGER PRIMARY KEY AUTOINCREMENT,
    name   TEXT    NOT NULL,
    email  TEXT    UNIQUE NOT NULL,
    cohort TEXT    NOT NULL,
    score  REAL    NOT NULL
);

CREATE TABLE IF NOT EXISTS courses (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    title      TEXT    NOT NULL,
    instructor TEXT    NOT NULL,
    credits    INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS enrollments (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id  INTEGER NOT NULL REFERENCES students(id),
    course_id   INTEGER NOT NULL REFERENCES courses(id),
    grade       TEXT    NOT NULL,
    enrolled_at TEXT    NOT NULL
);
"""

SEED_SQL = """
INSERT INTO students (name, email, cohort, score) VALUES
    ('Alice Chen',  'alice@lab.com',  'A1', 92),
    ('Bob Kim',     'bob@lab.com',    'A1', 85),
    ('Carol Wu',    'carol@lab.com',  'A1', 78),
    ('David Lee',   'david@lab.com',  'A1', 88),
    ('Eve Zhang',   'eve@lab.com',    'A1', 71),
    ('Frank Ho',    'frank@lab.com',  'A1', 95),
    ('Grace Liu',   'grace@lab.com',  'A2', 82),
    ('Henry Tan',   'henry@lab.com',  'A2', 67),
    ('Iris Wong',   'iris@lab.com',   'A2', 90),
    ('Jack Ma',     'jack@lab.com',   'A2', 75),
    ('Kara Ng',     'kara@lab.com',   'A2', 65),
    ('Leo Chen',    'leo@lab.com',    'A2', 88),
    ('Mia Park',    'mia@lab.com',    'B1', 80),
    ('Nate Liu',    'nate@lab.com',   'B1', 60),
    ('Olivia Wu',   'olivia@lab.com', 'B1', 75),
    ('Paul Kim',    'paul@lab.com',   'B1', 85),
    ('Quinn Lee',   'quinn@lab.com',  'B1', 70),
    ('Rose Ho',     'rose@lab.com',   'B1', 63);

INSERT INTO courses (title, instructor, credits) VALUES
    ('Python Basics',   'Dr. Smith',  3),
    ('Data Analysis',   'Dr. Jones',  3),
    ('Web Dev',         'Dr. Brown',  2),
    ('ML Fundamentals', 'Dr. Taylor', 4),
    ('SQL Mastery',     'Dr. Wilson', 2);

INSERT INTO enrollments (student_id, course_id, grade, enrolled_at) VALUES
    (1,  1, 'A', '2024-01-15'), (1,  2, 'A', '2024-01-15'),
    (2,  1, 'B', '2024-01-15'), (2,  3, 'B', '2024-01-16'),
    (3,  2, 'B', '2024-01-15'), (3,  4, 'C', '2024-01-17'),
    (4,  1, 'A', '2024-01-15'), (4,  5, 'A', '2024-01-18'),
    (5,  3, 'C', '2024-01-16'),
    (6,  1, 'A', '2024-01-15'),
    (7,  2, 'B', '2024-01-15'), (7,  5, 'B', '2024-01-18'),
    (8,  3, 'C', '2024-01-16'),
    (9,  4, 'A', '2024-01-17'), (9,  2, 'A', '2024-01-15'),
    (10, 1, 'B', '2024-01-15'), (10, 5, 'C', '2024-01-18'),
    (11, 3, 'D', '2024-01-16'), (11, 4, 'C', '2024-01-17'),
    (12, 2, 'A', '2024-01-15'), (12, 1, 'B', '2024-01-15'),
    (13, 1, 'B', '2024-01-15'), (13, 3, 'C', '2024-01-16'),
    (14, 4, 'D', '2024-01-17'),
    (15, 5, 'B', '2024-01-18'), (15, 2, 'B', '2024-01-15'),
    (16, 1, 'A', '2024-01-15'), (16, 4, 'B', '2024-01-17'),
    (17, 3, 'C', '2024-01-16'),
    (18, 5, 'D', '2024-01-18');
"""


def create_database(db_path: str = DB_PATH) -> str:
    if os.path.exists(db_path):
        os.remove(db_path)
    conn = sqlite3.connect(db_path)
    conn.executescript(SCHEMA_SQL)
    conn.executescript(SEED_SQL)
    conn.commit()
    conn.close()
    print(f"Database created: {db_path}")
    return db_path


if __name__ == "__main__":
    create_database()
```

- [ ] **Step 2: Run `init_db.py`**

```bash
cd implementation
python init_db.py
```

Expected:
```
Database created: /absolute/path/to/implementation/lab.db
```

- [ ] **Step 3: Verify row counts**

```bash
python -c "
import sqlite3
conn = sqlite3.connect('lab.db')
for t in ['students', 'courses', 'enrollments']:
    n = conn.execute(f'SELECT COUNT(*) FROM {t}').fetchone()[0]
    print(f'{t}: {n} rows')
conn.close()"
```

Expected:
```
students: 18 rows
courses: 5 rows
enrollments: 30 rows
```

- [ ] **Step 4: Commit**

```bash
git add implementation/init_db.py
git commit -m "feat: add database init with schema and seed data"
```

---

## Task 3: `db.py` — Core (ValidationError + SQLiteAdapter skeleton + introspection)

**Files:**
- Create: `implementation/db.py`

- [ ] **Step 1: Write `db.py` with all core methods**

```python
# implementation/db.py
import sqlite3

ALLOWED_OPERATORS = {"=", "!=", "<", ">", "<=", ">=", "LIKE", "IN"}
ALLOWED_METRICS   = {"count", "avg", "sum", "min", "max"}


class ValidationError(Exception):
    """Raised when user input fails validation before any SQL is built."""


class SQLiteAdapter:
    def __init__(self, db_path: str):
        self.db_path = db_path

    # ── connection ────────────────────────────────────────────────────────────

    def connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    # ── introspection ─────────────────────────────────────────────────────────

    def list_tables(self) -> list[str]:
        conn = self.connect()
        try:
            cur = conn.execute(
                "SELECT name FROM sqlite_master "
                "WHERE type='table' AND name NOT LIKE 'sqlite_%'"
            )
            return [row[0] for row in cur.fetchall()]
        finally:
            conn.close()

    def get_table_schema(self, table: str) -> list[dict]:
        conn = self.connect()
        try:
            cur = conn.execute(f'PRAGMA table_info("{table}")')
            return [
                {
                    "name":    row["name"],
                    "type":    row["type"],
                    "pk":      bool(row["pk"]),
                    "notnull": bool(row["notnull"]),
                }
                for row in cur.fetchall()
            ]
        finally:
            conn.close()

    def get_full_schema(self) -> dict:
        return {
            "tables": {
                t: {"columns": self.get_table_schema(t)}
                for t in self.list_tables()
            }
        }

    # ── private validators ────────────────────────────────────────────────────

    def _get_column_names(self, table: str) -> set[str]:
        return {col["name"] for col in self.get_table_schema(table)}

    def _validate_table(self, table: str) -> None:
        if table not in self.list_tables():
            raise ValidationError(f"Unknown table: '{table}'")

    def _validate_columns(self, table: str, columns: list[str]) -> None:
        valid = self._get_column_names(table)
        for col in columns:
            if col not in valid:
                raise ValidationError(
                    f"Unknown column: '{col}' in table '{table}'"
                )

    def _validate_operator(self, op: str) -> None:
        if op.upper() not in {o.upper() for o in ALLOWED_OPERATORS}:
            raise ValidationError(
                f"Unsupported operator: '{op}'. "
                f"Allowed: {', '.join(sorted(ALLOWED_OPERATORS))}"
            )

    def _build_where(
        self, table: str, filters: list[dict]
    ) -> tuple[str, list]:
        """Build a safe WHERE clause from a list of filter dicts.

        Each filter: {"column": str, "op": str, "value": any}
        Returns (WHERE clause string, params list).
        Returns ("", []) when filters is empty.
        """
        if not filters:
            return "", []

        clauses, params = [], []
        for f in filters:
            col = f["column"]
            op  = f["op"].upper()
            val = f["value"]
            self._validate_columns(table, [col])
            self._validate_operator(op)

            if op == "IN":
                vals = val if isinstance(val, list) else [val]
                clauses.append(f'"{col}" IN ({",".join("?" * len(vals))})')
                params.extend(vals)
            else:
                clauses.append(f'"{col}" {op} ?')
                params.append(val)

        return "WHERE " + " AND ".join(clauses), params

    # ── public query methods (added in Tasks 4-6) ─────────────────────────────
    # search(), insert(), aggregate() follow below
```

- [ ] **Step 2: Commit the skeleton**

```bash
git add implementation/db.py
git commit -m "feat: add SQLiteAdapter skeleton with core validation methods"
```

---

## Task 4: Tests for core methods

**Files:**
- Create: `implementation/tests/test_server.py`

- [ ] **Step 1: Write `tests/test_server.py` with fixture + TestCore**

```python
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
```

- [ ] **Step 2: Run tests — all should PASS**

```bash
cd implementation
pytest tests/test_server.py::TestCore -v
```

Expected:
```
PASSED tests/test_server.py::TestCore::test_list_tables
PASSED tests/test_server.py::TestCore::test_get_table_schema
PASSED tests/test_server.py::TestCore::test_get_full_schema
PASSED tests/test_server.py::TestCore::test_validate_table_unknown
PASSED tests/test_server.py::TestCore::test_validate_columns_unknown
PASSED tests/test_server.py::TestCore::test_validate_operator_unknown
6 passed
```

- [ ] **Step 3: Commit**

```bash
git add implementation/tests/test_server.py
git commit -m "test: add TestCore for SQLiteAdapter core validation"
```

---

## Task 5: `db.py` — `search()` with TDD

**Files:**
- Modify: `implementation/tests/test_server.py` (append TestSearch)
- Modify: `implementation/db.py` (add search method)

- [ ] **Step 1: Append TestSearch to `tests/test_server.py`**

Add after the TestCore class:

```python
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
```

- [ ] **Step 2: Run tests — should FAIL (search not yet defined)**

```bash
pytest tests/test_server.py::TestSearch -v
```

Expected: `AttributeError: 'SQLiteAdapter' object has no attribute 'search'`

- [ ] **Step 3: Add `search()` to `db.py`**

Add this method to `SQLiteAdapter` (after `_build_where`):

```python
    def search(
        self,
        table: str,
        columns: list[str] | None = None,
        filters: list[dict] | None = None,
        limit: int = 20,
        offset: int = 0,
        order_by: str | None = None,
        descending: bool = False,
    ) -> dict:
        self._validate_table(table)

        if columns:
            self._validate_columns(table, columns)
            col_clause = ", ".join(f'"{c}"' for c in columns)
        else:
            col_clause = "*"

        where_clause, params = self._build_where(table, filters or [])

        order_clause = ""
        if order_by:
            self._validate_columns(table, [order_by])
            direction = "DESC" if descending else "ASC"
            order_clause = f'ORDER BY "{order_by}" {direction}'

        sql = (
            f'SELECT {col_clause} FROM "{table}" '
            f'{where_clause} {order_clause} '
            f'LIMIT ? OFFSET ?'
        )
        params.extend([limit, offset])

        conn = self.connect()
        try:
            cur = conn.execute(sql, params)
            rows = [dict(row) for row in cur.fetchall()]
            return {"rows": rows, "total": len(rows), "table": table}
        finally:
            conn.close()
```

- [ ] **Step 4: Run tests — all should PASS**

```bash
pytest tests/test_server.py::TestSearch -v
```

Expected: `9 passed`

- [ ] **Step 5: Commit**

```bash
git add implementation/db.py implementation/tests/test_server.py
git commit -m "feat: implement search() with filters, ordering, pagination"
```

---

## Task 6: `db.py` — `insert()` with TDD

**Files:**
- Modify: `implementation/tests/test_server.py` (append TestInsert)
- Modify: `implementation/db.py` (add insert method)

- [ ] **Step 1: Append TestInsert to `tests/test_server.py`**

```python
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
```

- [ ] **Step 2: Run tests — should FAIL**

```bash
pytest tests/test_server.py::TestInsert -v
```

Expected: `AttributeError: 'SQLiteAdapter' object has no attribute 'insert'`

- [ ] **Step 3: Add `insert()` to `db.py`**

```python
    def insert(self, table: str, values: dict) -> dict:
        self._validate_table(table)
        if not values:
            raise ValidationError("Insert values cannot be empty")
        self._validate_columns(table, list(values.keys()))

        cols         = list(values.keys())
        col_clause   = ", ".join(f'"{c}"' for c in cols)
        placeholders = ", ".join("?" * len(cols))
        params       = [values[c] for c in cols]

        sql = f'INSERT INTO "{table}" ({col_clause}) VALUES ({placeholders})'

        conn = self.connect()
        try:
            cur = conn.execute(sql, params)
            conn.commit()
            return {"inserted": values, "id": cur.lastrowid}
        finally:
            conn.close()
```

- [ ] **Step 4: Run tests — all should PASS**

```bash
pytest tests/test_server.py::TestInsert -v
```

Expected: `5 passed`

- [ ] **Step 5: Commit**

```bash
git add implementation/db.py implementation/tests/test_server.py
git commit -m "feat: implement insert() with validation and parameterized queries"
```

---

## Task 7: `db.py` — `aggregate()` with TDD

**Files:**
- Modify: `implementation/tests/test_server.py` (append TestAggregate)
- Modify: `implementation/db.py` (add aggregate method)

- [ ] **Step 1: Append TestAggregate to `tests/test_server.py`**

```python
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
```

- [ ] **Step 2: Run tests — should FAIL**

```bash
pytest tests/test_server.py::TestAggregate -v
```

Expected: `AttributeError: 'SQLiteAdapter' object has no attribute 'aggregate'`

- [ ] **Step 3: Add `aggregate()` to `db.py`**

```python
    def aggregate(
        self,
        table: str,
        metric: str,
        column: str | None = None,
        filters: list[dict] | None = None,
        group_by: str | None = None,
    ) -> dict:
        self._validate_table(table)

        metric_lower = metric.lower()
        if metric_lower not in ALLOWED_METRICS:
            raise ValidationError(
                f"Unsupported metric: '{metric}'. "
                f"Use: {', '.join(sorted(ALLOWED_METRICS))}"
            )
        if metric_lower in {"avg", "sum", "min", "max"} and not column:
            raise ValidationError(f"Metric '{metric}' requires a column")
        if column:
            self._validate_columns(table, [column])
        if group_by:
            self._validate_columns(table, [group_by])

        agg_expr = (
            f'{metric_lower.upper()}("{column}")' if column else "COUNT(*)"
        )
        where_clause, params = self._build_where(table, filters or [])

        if group_by:
            sql = (
                f'SELECT "{group_by}" AS grp, {agg_expr} AS value '
                f'FROM "{table}" {where_clause} '
                f'GROUP BY "{group_by}"'
            )
        else:
            sql = (
                f'SELECT {agg_expr} AS value '
                f'FROM "{table}" {where_clause}'
            )

        conn = self.connect()
        try:
            cur = conn.execute(sql, params)
            rows = [dict(row) for row in cur.fetchall()]
            return {"rows": rows, "metric": metric_lower, "table": table}
        finally:
            conn.close()
```

- [ ] **Step 4: Run the full test suite — all should PASS**

```bash
pytest tests/test_server.py -v
```

Expected: `TestCore (6) + TestSearch (9) + TestInsert (5) + TestAggregate (11) = 31 passed`

- [ ] **Step 5: Commit**

```bash
git add implementation/db.py implementation/tests/test_server.py
git commit -m "feat: implement aggregate() with count/avg/sum/min/max and group_by"
```

---

## Task 8: `mcp_server.py` — Tools + Resources + Transport flag

**Files:**
- Create: `implementation/mcp_server.py`

- [ ] **Step 1: Write `mcp_server.py`**

```python
# implementation/mcp_server.py
import json
import argparse
from pathlib import Path

from fastmcp import FastMCP
from db import SQLiteAdapter, ValidationError

DB_PATH = str(Path(__file__).parent / "lab.db")
adapter = SQLiteAdapter(DB_PATH)
mcp     = FastMCP("SQLite Lab MCP Server")


# ── tools ─────────────────────────────────────────────────────────────────────

@mcp.tool(name="search")
def search(
    table: str,
    filters: list | None = None,
    columns: list | None = None,
    limit: int = 20,
    offset: int = 0,
    order_by: str | None = None,
    descending: bool = False,
) -> str:
    """Search rows in a database table with optional filters, column selection,
    ordering, and pagination.

    Args:
        table:      Table name — students | courses | enrollments
        filters:    List of filter objects: [{"column": "cohort", "op": "=", "value": "A1"}]
                    Supported ops: =  !=  <  >  <=  >=  LIKE  IN
        columns:    Columns to return (returns all if omitted)
        limit:      Max rows to return (default 20)
        offset:     Skip N rows for pagination (default 0)
        order_by:   Column name to sort by
        descending: Sort descending when true (default false)
    """
    try:
        result = adapter.search(
            table=table, columns=columns, filters=filters,
            limit=limit, offset=offset,
            order_by=order_by, descending=descending,
        )
        return json.dumps(result, indent=2)
    except ValidationError as e:
        return json.dumps({"error": str(e)})


@mcp.tool(name="insert")
def insert(table: str, values: dict) -> str:
    """Insert a new row into a database table.

    Args:
        table:  Table name — students | courses | enrollments
        values: Column-value pairs, e.g. {"name": "Alice", "cohort": "B2", "score": 85}
    """
    try:
        result = adapter.insert(table=table, values=values)
        return json.dumps(result, indent=2)
    except ValidationError as e:
        return json.dumps({"error": str(e)})


@mcp.tool(name="aggregate")
def aggregate(
    table: str,
    metric: str,
    column: str | None = None,
    filters: list | None = None,
    group_by: str | None = None,
) -> str:
    """Run aggregate functions on a database table.

    Args:
        table:    Table name — students | courses | enrollments
        metric:   One of: count  avg  sum  min  max
        column:   Column to aggregate (required for avg / sum / min / max)
        filters:  Optional row filters (same format as search)
        group_by: Column name to group results by
    """
    try:
        result = adapter.aggregate(
            table=table, metric=metric, column=column,
            filters=filters, group_by=group_by,
        )
        return json.dumps(result, indent=2)
    except ValidationError as e:
        return json.dumps({"error": str(e)})


# ── resources ─────────────────────────────────────────────────────────────────

@mcp.resource("schema://database")
def database_schema() -> str:
    """Full schema of all database tables (students, courses, enrollments)."""
    return json.dumps(adapter.get_full_schema(), indent=2)


@mcp.resource("schema://table/{table_name}")
def table_schema(table_name: str) -> str:
    """Schema for a specific database table. Use table_name = students | courses | enrollments."""
    try:
        adapter._validate_table(table_name)
        cols = adapter.get_table_schema(table_name)
        return json.dumps({"table": table_name, "columns": cols}, indent=2)
    except ValidationError as e:
        return json.dumps({"error": str(e)})


# ── entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="SQLite Lab MCP Server")
    parser.add_argument(
        "--transport",
        default="stdio",
        choices=["stdio", "sse", "streamable-http"],
        help="Transport type (default: stdio)",
    )
    parser.add_argument(
        "--port", type=int, default=8000,
        help="Port for HTTP/SSE transport (default: 8000)",
    )
    args = parser.parse_args()

    if args.transport == "stdio":
        mcp.run()
    elif args.transport == "sse":
        mcp.run(transport="sse", host="0.0.0.0", port=args.port)
    else:
        mcp.run(transport="streamable-http", host="0.0.0.0", port=args.port)
```

- [ ] **Step 2: Smoke-test stdio startup**

```bash
cd implementation
echo '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"test","version":"1"}}}' | python mcp_server.py
```

Expected: a JSON response containing `"protocolVersion"` (may also contain an error — that is OK at this step; the important thing is the process starts and responds).

- [ ] **Step 3: Commit**

```bash
git add implementation/mcp_server.py
git commit -m "feat: add FastMCP server with search/insert/aggregate tools and schema resources"
```

---

## Task 9: `verify_server.py` — Manual verification script

**Files:**
- Create: `implementation/verify_server.py`

- [ ] **Step 1: Write `verify_server.py`**

```python
# implementation/verify_server.py
"""
Manual verification script for the SQLite MCP lab.
Imports SQLiteAdapter directly — the MCP server does NOT need to be running.

Usage:
    python verify_server.py
"""
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from db import SQLiteAdapter, ValidationError

DB_PATH = os.path.join(os.path.dirname(__file__), "lab.db")

P = "[PASS]"
F = "[FAIL]"


def main():
    if not os.path.exists(DB_PATH):
        print("ERROR: lab.db not found. Run: python init_db.py")
        sys.exit(1)

    adapter = SQLiteAdapter(DB_PATH)

    print("=" * 55)
    print("SQLite MCP Lab — Verification")
    print("=" * 55)

    # ── search ─────────────────────────────────────────────
    print("\n[search]")

    r = adapter.search("students", filters=[{"column": "cohort", "op": "=", "value": "A1"}])
    tag = P if r["total"] == 6 else F
    print(f"{tag} search students cohort=A1 → {r['total']} rows (expected 6)")

    r = adapter.search("students", order_by="score", descending=True, limit=3)
    scores = [row["score"] for row in r["rows"]]
    tag = P if scores == sorted(scores, reverse=True) else F
    print(f"{tag} search ORDER BY score DESC LIMIT 3 → {scores}")

    r = adapter.search("students", columns=["name", "cohort"], limit=2)
    tag = P if set(r["rows"][0].keys()) == {"name", "cohort"} else F
    print(f"{tag} search column selection → keys: {list(r['rows'][0].keys())}")

    # ── insert ─────────────────────────────────────────────
    print("\n[insert]")

    r = adapter.insert("students", {
        "name": "Verify Student", "email": "verify_unique_999@lab.com",
        "cohort": "B2", "score": 77.0,
    })
    tag = P if r.get("id") is not None else F
    print(f"{tag} insert new student → id={r.get('id')}, name={r['inserted']['name']}")

    # ── aggregate ──────────────────────────────────────────
    print("\n[aggregate]")

    r = adapter.aggregate("students", "count")
    tag = P if r["rows"][0]["value"] >= 18 else F
    print(f"{tag} aggregate count students → {r['rows'][0]['value']}")

    r = adapter.aggregate("students", "avg", column="score")
    avg_val = r["rows"][0]["value"]
    tag = P if isinstance(avg_val, (int, float)) else F
    print(f"{tag} aggregate avg score → {avg_val:.2f}")

    r = adapter.aggregate("students", "count", group_by="cohort")
    tag = P if len(r["rows"]) >= 3 else F
    print(f"{tag} aggregate count by cohort → {len(r['rows'])} groups")
    for row in sorted(r["rows"], key=lambda x: x["grp"]):
        print(f"       {row['grp']}: {row['value']}")

    # ── resources ──────────────────────────────────────────
    print("\n[resources]")

    schema = adapter.get_full_schema()
    tag = P if all(t in schema["tables"] for t in ["students", "courses", "enrollments"]) else F
    print(f"{tag} schema://database → tables: {list(schema['tables'].keys())}")

    cols = adapter.get_table_schema("students")
    tag = P if any(c["name"] == "cohort" for c in cols) else F
    print(f"{tag} schema://table/students → columns: {[c['name'] for c in cols]}")

    # ── error handling ─────────────────────────────────────
    print("\n[error handling]")

    try:
        adapter.search("nonexistent_table")
        print(f"{F} search unknown table → no error raised")
    except ValidationError as e:
        print(f"{P} search unknown table → {e}")

    try:
        adapter.search("students", filters=[{"column": "bad_col", "op": "=", "value": "x"}])
        print(f"{F} search unknown column → no error raised")
    except ValidationError as e:
        print(f"{P} search unknown column → {e}")

    try:
        adapter.search("students", filters=[{"column": "name", "op": "DROP TABLE", "value": "x"}])
        print(f"{F} bad operator → no error raised")
    except ValidationError as e:
        print(f"{P} bad operator → {e}")

    try:
        adapter.insert("students", {})
        print(f"{F} insert empty values → no error raised")
    except ValidationError as e:
        print(f"{P} insert empty values → {e}")

    try:
        adapter.aggregate("students", "drop_table")
        print(f"{F} aggregate bad metric → no error raised")
    except ValidationError as e:
        print(f"{P} aggregate bad metric → {e}")

    try:
        adapter.aggregate("students", "avg")
        print(f"{F} aggregate avg without column → no error raised")
    except ValidationError as e:
        print(f"{P} aggregate avg without column → {e}")

    print("\n" + "=" * 55)
    print("Verification complete.")
    print("=" * 55)


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Run `verify_server.py` — all lines should show `[PASS]`**

```bash
cd implementation
python verify_server.py
```

Expected output:
```
=======================================================
SQLite MCP Lab — Verification
=======================================================

[search]
[PASS] search students cohort=A1 → 6 rows (expected 6)
[PASS] search ORDER BY score DESC LIMIT 3 → [95, 92, 90]
[PASS] search column selection → keys: ['name', 'cohort']

[insert]
[PASS] insert new student → id=19, name=Verify Student

[aggregate]
[PASS] aggregate count students → 19
[PASS] aggregate avg score → 78.XX
[PASS] aggregate count by cohort → 3 groups
       A1: 6
       A2: 6
       B1: 6

[resources]
[PASS] schema://database → tables: ['students', 'courses', 'enrollments']
[PASS] schema://table/students → columns: ['id', 'name', 'email', 'cohort', 'score']

[error handling]
[PASS] search unknown table → Unknown table: 'nonexistent_table'
[PASS] search unknown column → Unknown column: 'bad_col' in table 'students'
[PASS] bad operator → Unsupported operator: 'DROP TABLE'. Allowed: ...
[PASS] insert empty values → Insert values cannot be empty
[PASS] aggregate bad metric → Unsupported metric: 'drop_table'. Use: avg, count, max, min, sum
[PASS] aggregate avg without column → Metric 'avg' requires a column

=======================================================
Verification complete.
=======================================================
```

- [ ] **Step 3: Commit**

```bash
git add implementation/verify_server.py
git commit -m "feat: add verify_server.py for manual CLI verification"
```

---

## Task 10: Client Config + README Quick Start

**Files:**
- Create: `.mcp.json` (repo root)
- Modify: `README.md` (add Quick Start section)

- [ ] **Step 1: Get the absolute path to `mcp_server.py`**

```bash
# Windows PowerShell:
(Resolve-Path implementation/mcp_server.py).Path

# macOS/Linux:
realpath implementation/mcp_server.py
```

Copy the output — you will paste it in the next step.

- [ ] **Step 2: Create `.mcp.json` at repo root**

Replace `PASTE_ABSOLUTE_PATH_HERE` with the path from Step 1:

```json
{
  "mcpServers": {
    "sqlite-lab": {
      "type": "stdio",
      "command": "python",
      "args": ["PASTE_ABSOLUTE_PATH_HERE"],
      "env": {}
    }
  }
}
```

- [ ] **Step 3: Add Quick Start section to `README.md`**

Insert the following immediately after the "## Goal" section in `README.md`:

```markdown
## Quick Start

### 1. Install

```bash
cd implementation
python -m venv .venv
.venv\Scripts\activate   # Windows
# source .venv/bin/activate  # macOS/Linux
pip install -r requirements.txt
```

### 2. Initialize the database

```bash
python init_db.py
# → Database created: .../implementation/lab.db
```

### 3. Verify (no server needed)

```bash
python verify_server.py   # all [PASS]
```

### 4. Run automated tests

```bash
pytest tests/ -v
```

### 5. Run MCP Inspector

```bash
npx -y @modelcontextprotocol/inspector python ABSOLUTE_PATH/implementation/mcp_server.py
# open http://localhost:5173
```

### 6. Connect Claude Code

Edit `.mcp.json` at the repo root with the absolute path to `mcp_server.py`, then start Claude Code.

Reference the schema: `@sqlite-lab:schema://database`

### 7. HTTP transport (bonus)

```bash
python implementation/mcp_server.py --transport streamable-http
# server on http://0.0.0.0:8000
```
```

- [ ] **Step 4: Run `pytest tests/ -v` one final time to confirm green**

```bash
cd implementation
pytest tests/ -v
```

Expected: all 31 tests PASS.

- [ ] **Step 5: Commit everything**

```bash
git add .mcp.json README.md
git commit -m "docs: add quick start guide and .mcp.json client config"
```

---

## Demo Video Checklist

Run these in order during the recording:

| # | Command / Action | What to show |
|---|-----------------|-------------|
| 1 | `python init_db.py` | DB created, row counts |
| 2 | `python verify_server.py` | All `[PASS]` lines |
| 3 | `pytest tests/ -v` | 31 tests pass |
| 4 | MCP Inspector — start | Show 3 tools + 2 resources in sidebar |
| 5 | Inspector → `search` students cohort=A1 | 6 rows returned |
| 6 | Inspector → `insert` new student | `{"id": ..., "inserted": {...}}` |
| 7 | Inspector → `aggregate` avg score by cohort | Table of A1/A2/B1 averages |
| 8 | Inspector → `search` unknown table | `{"error": "Unknown table: 'xyz'"}` |
| 9 | Inspector → `schema://database` resource | Full schema JSON |
| 10 | Claude Code → `@sqlite-lab:schema://database` | Schema appears in context |
| 11 | Claude Code → "show me all A1 students" | Uses search tool automatically |

---

## Rubric Coverage Check

| Rubric Item | Points | Covered by |
|-------------|--------|-----------|
| Server starts successfully | 5 | Task 8 (mcp_server.py stdio) |
| Clean project structure | 5 | Tasks 1-10 file layout |
| Reproducible DB init | 5 | Task 2 (init_db.py) |
| DB/server code split | 5 | db.py vs mcp_server.py |
| `search` with filters/order/pagination | 10 | Task 5 |
| `insert` with returned payload | 10 | Task 6 |
| `aggregate` count/avg/sum/min/max | 10 | Task 7 |
| Full schema resource | 8 | Task 8 |
| Per-table schema template | 7 | Task 8 |
| Invalid table/column rejected | 5 | Tasks 3-7 (ValidationError) |
| Bad operator/metric rejected | 5 | Tasks 3, 5, 7 |
| Parameterized SQL (no injection) | 5 | Task 3 (_build_where) |
| Tool discovery verified | 4 | Task 9 + Inspector demo |
| Valid calls demonstrated | 3 | verify_server.py + Inspector |
| Invalid calls show clear errors | 3 | verify_server.py + Inspector |
| Client configured correctly | 4 | Task 10 (.mcp.json) |
| README with setup steps | 3 | Task 10 |
| Demo/screenshots | 3 | Demo video checklist |
| **Base total** | **100** | |
| HTTP transport (bonus) | +5 | Task 8 (--transport flag) |
