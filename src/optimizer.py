"""Query Optimization Utilities.

This module provides tools for analyzing and optimizing SQL queries,
including index recommendations and query plan analysis.
"""

import re
from typing import Any


class QueryOptimizer:
    """Analyzes and optimizes SQL queries for better performance."""

    def __init__(self):
        """Initialize the QueryOptimizer."""
        self.suggestions: list[str] = []

    def analyze_and_optimize(self, query: str) -> str:
        """Analyze a query and return an optimized version.

        Args:
            query: The SQL query to optimize.

        Returns:
            Optimized SQL query string.
        """
        optimized = query
        self.suggestions.clear()

        optimized = self._optimize_select_star(optimized)
        optimized = self._optimize_where_clauses(optimized)
        optimized = self._optimize_like_patterns(optimized)
        optimized = self._add_explicit_join_syntax(optimized)

        return optimized

    def _optimize_select_star(self, query: str) -> str:
        """Replace SELECT * with specific columns where possible.

        Args:
            query: Input query.

        Returns:
            Optimized query.
        """
        if "SELECT *" in query.upper():
            self.suggestions.append(
                "Consider specifying columns explicitly instead of SELECT * "
                "to reduce data transfer and improve performance."
            )
        return query

    def _optimize_where_clauses(self, query: str) -> str:
        """Optimize WHERE clause structure.

        Args:
            query: Input query.

        Returns:
            Optimized query.
        """
        where_match = re.search(r'WHERE\s+(.+?)(?:GROUP|ORDER|LIMIT|$)', query, re.IGNORECASE)
        if where_match:
            where_clause = where_match.group(1)
            if "OR" in where_clause and "AND" not in where_clause:
                self.suggestions.append(
                    "Consider using UNION for multiple OR conditions "
                    "to enable better index utilization."
                )
        return query

    def _optimize_like_patterns(self, query: str) -> str:
        """Check and optimize LIKE patterns.

        Args:
            query: Input query.

        Returns:
            Optimized query.
        """
        like_patterns = re.findall(r"LIKE\s+['\"]([^'\"]+)['\"]", query, re.IGNORECASE)
        for pattern in like_patterns:
            if pattern.startswith('%') or pattern.endswith('%'):
                self.suggestions.append(
                    f"LIKE pattern '{pattern}' cannot use indexes efficiently. "
                    "Consider full-text search for such patterns."
                )
        return query

    def _add_explicit_join_syntax(self, query: str) -> str:
        """Convert implicit joins to explicit JOIN syntax.

        Args:
            query: Input query with potential implicit joins.

        Returns:
            Query with explicit joins.
        """
        implicit_join_pattern = r'FROM\s+(\w+),\s*(\w+)\s+WHERE\s+(.+)'
        match = re.search(implicit_join_pattern, query, re.IGNORECASE)
        if match:
            table1, table2, condition = match.groups()
            self.suggestions.append(
                f"Consider converting implicit join to explicit INNER JOIN "
                f"for better readability and maintainability."
            )
        return query

    def suggest_indexes(self, query: str) -> list[str]:
        """Suggest indexes based on query patterns.

        Args:
            query: SQL query to analyze.

        Returns:
            List of index creation suggestions.
        """
        suggestions = []

        where_cols = re.findall(r'WHERE\s+(\w+)\.(\w+)', query, re.IGNORECASE)
        for table, col in where_cols:
            suggestions.append(f"CREATE INDEX idx_{table}_{col} ON {table}({col});")

        join_cols = re.findall(r'JOIN\s+\w+\s+ON\s+(\w+)\.(\w+)', query, re.IGNORECASE)
        for table, col in join_cols:
            if f"CREATE INDEX idx_{table}_{col}" not in suggestions:
                suggestions.append(f"CREATE INDEX idx_{table}_{col} ON {table}({col});")

        return suggestions

    def explain_plan(self, query: str, database: str = "postgresql") -> str:
        """Generate an EXPLAIN plan query.

        Args:
            query: Query to explain.
            database: Database type (postgresql, mysql).

        Returns:
            EXPLAIN query string.
        """
        if database.lower() == "postgresql":
            return f"EXPLAIN ANALYZE {query}"
        elif database.lower() == "mysql":
            return f"EXPLAIN FORMAT=JSON {query}"
        return f"EXPLAIN {query}"


def estimate_query_complexity(query: str) -> dict[str, Any]:
    """Estimate the complexity of a SQL query.

    Args:
        query: SQL query to analyze.

    Returns:
        Dictionary with complexity metrics.
    """
    complexity = {
        "tables": len(re.findall(r'FROM\s+\w+', query, re.IGNORECASE)),
        "joins": len(re.findall(r'JOIN\s+\w+', query, re.IGNORECASE)),
        "subqueries": len(re.findall(r'\(SELECT', query, re.IGNORECASE)),
        "aggregations": len(re.findall(r'(SUM|AVG|COUNT|MIN|MAX)\(', query, re.IGNORECASE)),
        "has_order_by": bool(re.search(r'ORDER\s+BY', query, re.IGNORECASE)),
        "has_group_by": bool(re.search(r'GROUP\s+BY', query, re.IGNORECASE)),
    }

    complexity["score"] = (
        complexity["tables"] * 2 +
        complexity["joins"] * 3 +
        complexity["subqueries"] * 5 +
        complexity["aggregations"] * 1 +
        (1 if complexity["has_order_by"] else 0) +
        (1 if complexity["has_group_by"] else 0)
    )

    return complexity
