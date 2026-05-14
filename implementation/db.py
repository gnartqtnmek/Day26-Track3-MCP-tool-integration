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

    # ── public query methods (added in Tasks 5-7) ─────────────────────────────

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

    # aggregate() will be added in a later task
