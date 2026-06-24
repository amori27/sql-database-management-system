"""Query Builder for Complex SQL Queries.

This module provides a fluent interface for building complex SQL queries
including joins, subqueries, aggregations, and window functions.
"""

from typing import Any


class QueryBuilder:
    """Fluent SQL query builder supporting complex queries."""

    def __init__(self):
        """Initialize the QueryBuilder."""
        self._select_columns: list[str] = []
        self._from_tables: list[str] = []
        self._join_clauses: list[str] = []
        self._where_conditions: list[str] = []
        self._group_by_columns: list[str] = []
        self._having_conditions: list[str] = []
        self._order_by_columns: list[str] = []
        self._limit_value: int | None = None
        self._offset_value: int | None = None

    def select(self, *columns: str) -> "QueryBuilder":
        """Add SELECT columns.

        Args:
            *columns: Column names to select.

        Returns:
            Self for method chaining.
        """
        self._select_columns.extend(columns)
        return self

    def from_table(self, table: str) -> "QueryBuilder":
        """Set the FROM table.

        Args:
            table: Table name.

        Returns:
            Self for method chaining.
        """
        self._from_tables.append(table)
        return self

    def join(
        self,
        table: str,
        condition: str,
        join_type: str = "INNER"
    ) -> "QueryBuilder":
        """Add a JOIN clause.

        Args:
            table: Table to join.
            condition: Join condition (ON clause).
            join_type: Type of join (INNER, LEFT, RIGHT, FULL).

        Returns:
            Self for method chaining.
        """
        self._join_clauses.append(f"{join_type} JOIN {table} ON {condition}")
        return self

    def where(self, condition: str) -> "QueryBuilder":
        """Add a WHERE condition.

        Args:
            condition: WHERE condition expression.

        Returns:
            Self for method chaining.
        """
        self._where_conditions.append(condition)
        return self

    def group_by(self, *columns: str) -> "QueryBuilder":
        """Add GROUP BY columns.

        Args:
            *columns: Column names to group by.

        Returns:
            Self for method chaining.
        """
        self._group_by_columns.extend(columns)
        return self

    def having(self, condition: str) -> "QueryBuilder":
        """Add a HAVING condition.

        Args:
            condition: HAVING condition expression.

        Returns:
            Self for method chaining.
        """
        self._having_conditions.append(condition)
        return self

    def order_by(self, column: str, direction: str = "ASC") -> "QueryBuilder":
        """Add ORDER BY clause.

        Args:
            column: Column to order by.
            direction: Sort direction (ASC or DESC).

        Returns:
            Self for method chaining.
        """
        self._order_by_columns.append(f"{column} {direction}")
        return self

    def limit(self, value: int) -> "QueryBuilder":
        """Add LIMIT clause.

        Args:
            value: Maximum number of rows.

        Returns:
            Self for method chaining.
        """
        self._limit_value = value
        return self

    def offset(self, value: int) -> "QueryBuilder":
        """Add OFFSET clause.

        Args:
            value: Number of rows to skip.

        Returns:
            Self for method chaining.
        """
        self._offset_value = value
        return self

    def select_with_joins(
        self,
        tables: list[str],
        columns: list[str],
        conditions: list[str] | None = None
    ) -> str:
        """Build a SELECT with multiple joins.

        Args:
            tables: List of table names.
            columns: Columns to select.
            conditions: Optional join conditions.

        Returns:
            SQL query string.
        """
        self._from_tables = tables[:1] if tables else []
        for i in range(1, len(tables)):
            if conditions and i - 1 < len(conditions):
                self.join(tables[i], conditions[i - 1])

        self.select(*columns)
        return self.build()

    def build(self) -> str:
        """Build the final SQL query string.

        Returns:
            Complete SQL query.
        """
        parts = ["SELECT"]

        if self._select_columns:
            parts.append(", ".join(self._select_columns))
        else:
            parts.append("*")

        if self._from_tables:
            parts.append(f"FROM {', '.join(self._from_tables)}")

        if self._join_clauses:
            parts.append(" ".join(self._join_clauses))

        if self._where_conditions:
            parts.append(f"WHERE {' AND '.join(self._where_conditions)}")

        if self._group_by_columns:
            parts.append(f"GROUP BY {', '.join(self._group_by_columns)}")

        if self._having_conditions:
            parts.append(f"HAVING {' AND '.join(self._having_conditions)}")

        if self._order_by_columns:
            parts.append(f"ORDER BY {', '.join(self._order_by_columns)}")

        if self._limit_value is not None:
            parts.append(f"LIMIT {self._limit_value}")

        if self._offset_value is not None:
            parts.append(f"OFFSET {self._offset_value}")

        return " ".join(parts)

    def reset(self) -> None:
        """Reset the builder state."""
        self._select_columns.clear()
        self._from_tables.clear()
        self._join_clauses.clear()
        self._where_conditions.clear()
        self._group_by_columns.clear()
        self._having_conditions.clear()
        self._order_by_columns.clear()
        self._limit_value = None
        self._offset_value = None


def build_aggregation_query(
    table: str,
    group_column: str,
    agg_column: str,
    agg_function: str = "SUM"
) -> str:
    """Build an aggregation query.

    Args:
        table: Table name.
        group_column: Column to group by.
        agg_column: Column to aggregate.
        agg_function: Aggregation function (SUM, AVG, COUNT, MIN, MAX).

    Returns:
        SQL aggregation query string.
    """
    return f"""
    SELECT {group_column}, {agg_function}({agg_column}) as result
    FROM {table}
    GROUP BY {group_column}
    HAVING {agg_function}({agg_column}) > 0
    ORDER BY result DESC
    """


def build_window_query(
    table: str,
    partition_col: str,
    order_col: str,
    window_func: str = "ROW_NUMBER"
) -> str:
    """Build a window function query.

    Args:
        table: Table name.
        partition_col: Column to partition by.
        order_col: Column to order by within partition.
        window_func: Window function to use.

    Returns:
        SQL window function query string.
    """
    return f"""
    SELECT *,
        {window_func}() OVER (PARTITION BY {partition_col} ORDER BY {order_col}) as row_idx
    FROM {table}
    """
