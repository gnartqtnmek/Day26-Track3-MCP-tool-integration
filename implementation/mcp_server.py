# implementation/mcp_server.py
import json
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

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
