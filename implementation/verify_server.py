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
