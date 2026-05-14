# Design: FastMCP + SQLite MCP Server Lab

**Date:** 2026-05-14  
**Scope:** Implement `implementation/` from scratch based on pseudocode skeletons in `pseudocode/`

---

## 1. Architecture

### Approach: 2-file split (Approach B)

```
implementation/
├── db.py              # SQLiteAdapter: connect, validate identifiers, search, insert, aggregate
├── init_db.py         # Create lab.db, define schema SQL, seed data
├── mcp_server.py      # FastMCP server: tools + resources, imports SQLiteAdapter from db.py
├── verify_server.py   # Manual verification script: calls each tool, prints PASS/FAIL
└── tests/
    └── test_server.py # pytest: tool discovery, valid calls, invalid/error calls
```

### Data flow

```
MCP Client (Claude Code CLI / MCP Inspector)
    ↓ stdio  OR  HTTP (port 8000 with --transport http flag)
mcp_server.py  →  SQLiteAdapter (db.py)
                      ↓
                   lab.db (SQLite file, created by init_db.py)
```

### Dependency rules

- `mcp_server.py` imports `SQLiteAdapter` from `db.py` — never writes SQL directly
- `init_db.py` is standalone, run once to create `lab.db`
- `verify_server.py` imports tool functions directly from `mcp_server.py` for fast testing without MCP protocol
- `tests/test_server.py` tests `SQLiteAdapter` methods directly against in-memory SQLite

---

## 2. Data Model

### Schema

```sql
CREATE TABLE students (
    id      INTEGER PRIMARY KEY AUTOINCREMENT,
    name    TEXT NOT NULL,
    email   TEXT UNIQUE NOT NULL,
    cohort  TEXT NOT NULL,
    score   REAL NOT NULL
);

CREATE TABLE courses (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    title      TEXT NOT NULL,
    instructor TEXT NOT NULL,
    credits    INTEGER NOT NULL
);

CREATE TABLE enrollments (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id  INTEGER NOT NULL REFERENCES students(id),
    course_id   INTEGER NOT NULL REFERENCES courses(id),
    grade       TEXT NOT NULL,
    enrolled_at TEXT NOT NULL
);
```

### Seed data

- 18 students across 3 cohorts: `A1` (6), `A2` (6), `B1` (6)
- Scores range 60–100, distributed so per-cohort averages differ meaningfully
- 5 courses: Python Basics, Data Analysis, Web Dev, ML Fundamentals, SQL Mastery
- 30 enrollments: each student in 1–2 courses, grades A/B/C/D

---

## 3. Tools

### `search`

```python
search(
    table: str,
    filters: list[dict] | None = None,   # [{"column": "cohort", "op": "=", "value": "A1"}]
    columns: list[str] | None = None,
    limit: int = 20,
    offset: int = 0,
    order_by: str | None = None,
    descending: bool = False
) -> dict
# Returns: {"rows": [...], "total": N, "table": "students"}
```

Allowed filter operators: `=`, `!=`, `<`, `>`, `<=`, `>=`, `LIKE`, `IN`

### `insert`

```python
insert(
    table: str,
    values: dict   # {"name": "Alice", "cohort": "B2", "score": 85}
) -> dict
# Returns: {"inserted": {...}, "id": 19}
```

### `aggregate`

```python
aggregate(
    table: str,
    metric: str,                          # count | avg | sum | min | max
    column: str | None = None,
    filters: list[dict] | None = None,
    group_by: str | None = None
) -> dict
# Returns: {"rows": [{"group": "A1", "value": 78.5}, ...]}
```

`column` is required for `avg`, `sum`, `min`, `max`; ignored for `count`.

---

## 4. Resources

### `schema://database`

Returns full schema of all tables as JSON:

```json
{
  "tables": {
    "students": {
      "columns": [
        {"name": "id", "type": "INTEGER", "pk": true, "notnull": true},
        ...
      ]
    }
  }
}
```

Claude Code reference: `@sqlite-lab:schema://database`

### `schema://table/{table_name}`

Returns schema for a single table. Returns error string if table unknown.

Claude Code reference: `@sqlite-lab:schema://table/students`

---

## 5. Validation & Error Handling

All validation happens inside `SQLiteAdapter` before any SQL is built.

| Condition | Error message |
|-----------|--------------|
| Table does not exist | `"Unknown table: 'xyz'"` |
| Column does not exist | `"Unknown column: 'xyz' in table 'students'"` |
| Unsupported filter operator | `"Unsupported operator: 'DROP'. Allowed: =, !=, <, >, <=, >=, LIKE, IN"` |
| Unsupported metric | `"Unsupported metric: 'xyz'. Use: count, avg, sum, min, max"` |
| `avg`/`sum`/`min`/`max` without column | `"Metric 'avg' requires a column"` |
| Empty insert values | `"Insert values cannot be empty"` |

All identifiers (table names, column names) are validated against DB introspection — never interpolated raw into SQL. Values use parameterized queries (`?` placeholders).

---

## 6. Testing Strategy

### `verify_server.py` (manual, for video demo)

Runs sequentially without MCP protocol. Prints `[PASS]` / `[FAIL]` per case:

```
[PASS] search: students cohort=A1 → 6 rows
[PASS] insert: new student Alice  → id=19
[PASS] aggregate: avg score       → 78.5
[PASS] resource: schema://database → 3 tables
[PASS] error: search unknown_table → "Unknown table: 'xyz'"
[PASS] error: insert empty values  → "Insert values cannot be empty"
```

### `tests/test_server.py` (pytest, for rubric)

Three test classes:
- `TestSearch`: valid filter, pagination, unknown table, unknown column, bad operator
- `TestInsert`: valid insert, empty values, unknown table, unknown column
- `TestAggregate`: count, avg with group_by, missing column for avg, bad metric

Each test uses a fresh in-memory SQLite DB (`:memory:`) seeded in a `pytest.fixture`.

---

## 7. Transport

| Mode | Command | Used by |
|------|---------|---------|
| stdio (default) | `python mcp_server.py` | Claude Code, MCP Inspector |
| HTTP (bonus) | `python mcp_server.py --transport http` | Browser, curl, bonus demo |

Transport flag parsed via `argparse`. HTTP runs on port 8000. No auth required for stdio; bonus auth not in scope for base implementation.

---

## 8. Client Configuration

### Claude Code `.mcp.json`

```json
{
  "mcpServers": {
    "sqlite-lab": {
      "type": "stdio",
      "command": "python",
      "args": ["ABSOLUTE_PATH/implementation/mcp_server.py"],
      "env": {}
    }
  }
}
```

### MCP Inspector

```bash
npx -y @modelcontextprotocol/inspector python ABSOLUTE_PATH/implementation/mcp_server.py
```

---

## 9. Demo Video Checklist

1. `python init_db.py` — show DB created
2. `python verify_server.py` — all PASS
3. MCP Inspector: show 3 tools + 2 resources discovered
4. Inspector: call `search` students cohort=A1 → 6 rows
5. Inspector: call `insert` new student → id returned
6. Inspector: call `aggregate` avg score by cohort → table of results
7. Inspector: call `search` with unknown table → clear error
8. Claude Code: `@sqlite-lab:schema://database` → full schema
9. Claude Code: ask "show me all students in cohort A1" → uses search tool
10. `pytest tests/` — all tests pass

---

## Rubric Coverage

| Section | Points | Covered by |
|---------|--------|-----------|
| Server Foundation | 20 | `mcp_server.py` starts, clean structure, `init_db.py` reproducible, db/server split |
| Required Tools | 30 | `search`, `insert`, `aggregate` fully implemented |
| MCP Resources | 15 | `schema://database`, `schema://table/{name}` |
| Safety & Error Handling | 15 | Validation in `SQLiteAdapter`, parameterized queries |
| Verification | 10 | `verify_server.py` + `tests/test_server.py` |
| Client Integration | 10 | Claude Code config + Inspector demo |
| **Total** | **100** | |
| Bonus HTTP transport | +5 | `--transport http` flag |
