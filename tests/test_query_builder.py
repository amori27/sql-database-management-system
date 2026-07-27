"""Tests for SQL query builder."""

from src.query_builder import (
    QueryBuilder,
    build_aggregation_query,
    build_window_query,
)


class TestQueryBuilderBasic:
    """Test basic QueryBuilder operations."""

    def test_select_single_column(self):
        q = QueryBuilder().select("id").from_table("users").build()
        assert q == "SELECT id FROM users"

    def test_select_multiple_columns(self):
        q = QueryBuilder().select("id", "name", "email").from_table("users").build()
        assert q == "SELECT id, name, email FROM users"

    def test_select_star_default(self):
        q = QueryBuilder().from_table("users").build()
        assert q == "SELECT * FROM users"

    def test_where_clause(self):
        q = (
            QueryBuilder()
            .select("id")
            .from_table("users")
            .where("id = 1")
            .build()
        )
        assert "WHERE id = 1" in q

    def test_multiple_where_clauses(self):
        q = (
            QueryBuilder()
            .select("id")
            .from_table("users")
            .where("id > 0")
            .where("active = 1")
            .build()
        )
        assert "WHERE id > 0 AND active = 1" in q

    def test_limit(self):
        q = (
            QueryBuilder()
            .select("id")
            .from_table("users")
            .limit(10)
            .build()
        )
        assert "LIMIT 10" in q

    def test_offset(self):
        q = (
            QueryBuilder()
            .select("id")
            .from_table("users")
            .offset(20)
            .build()
        )
        assert "OFFSET 20" in q

    def test_limit_and_offset(self):
        q = (
            QueryBuilder()
            .select("id")
            .from_table("users")
            .limit(10)
            .offset(20)
            .build()
        )
        assert "LIMIT 10" in q
        assert "OFFSET 20" in q

    def test_order_by_asc(self):
        q = (
            QueryBuilder()
            .select("id")
            .from_table("users")
            .order_by("name")
            .build()
        )
        assert "ORDER BY name ASC" in q

    def test_order_by_desc(self):
        q = (
            QueryBuilder()
            .select("id")
            .from_table("users")
            .order_by("name", "DESC")
            .build()
        )
        assert "ORDER BY name DESC" in q


class TestQueryBuilderJoins:
    """Test QueryBuilder join operations."""

    def test_inner_join(self):
        q = (
            QueryBuilder()
            .select("users.id", "orders.total")
            .from_table("users")
            .join("orders", "users.id = orders.user_id")
            .build()
        )
        assert "INNER JOIN orders ON users.id = orders.user_id" in q

    def test_left_join(self):
        q = (
            QueryBuilder()
            .select("users.id")
            .from_table("users")
            .join("orders", "users.id = orders.user_id", "LEFT")
            .build()
        )
        assert "LEFT JOIN orders ON users.id = orders.user_id" in q

    def test_right_join(self):
        q = (
            QueryBuilder()
            .select("users.id")
            .from_table("users")
            .join("orders", "users.id = orders.user_id", "RIGHT")
            .build()
        )
        assert "RIGHT JOIN orders ON users.id = orders.user_id" in q

    def test_multiple_joins(self):
        q = (
            QueryBuilder()
            .select("users.id", "orders.total", "products.name")
            .from_table("users")
            .join("orders", "users.id = orders.user_id")
            .join("products", "orders.product_id = products.id")
            .build()
        )
        assert "INNER JOIN orders" in q
        assert "INNER JOIN products" in q


class TestQueryBuilderGroupByHaving:
    """Test GROUP BY and HAVING clauses."""

    def test_group_by(self):
        q = (
            QueryBuilder()
            .select("dept", "COUNT(*)")
            .from_table("employees")
            .group_by("dept")
            .build()
        )
        assert "GROUP BY dept" in q

    def test_group_by_multiple(self):
        q = (
            QueryBuilder()
            .select("dept", "role", "COUNT(*)")
            .from_table("employees")
            .group_by("dept", "role")
            .build()
        )
        assert "GROUP BY dept, role" in q

    def test_having(self):
        q = (
            QueryBuilder()
            .select("dept", "COUNT(*)")
            .from_table("employees")
            .group_by("dept")
            .having("COUNT(*) > 5")
            .build()
        )
        assert "HAVING COUNT(*) > 5" in q


class TestQueryBuilderReset:
    """Test QueryBuilder reset functionality."""

    def test_reset_clears_all(self):
        q = (
            QueryBuilder()
            .select("id")
            .from_table("users")
            .where("id = 1")
            .limit(10)
        )
        q.reset()
        result = q.build()
        assert result == "SELECT *"

    def test_method_chaining_returns_self(self):
        q = QueryBuilder()
        assert q.select("id") is q
        assert q.from_table("users") is q
        assert q.where("id = 1") is q
        assert q.limit(10) is q
        assert q.offset(0) is q
        assert q.order_by("id") is q
        assert q.group_by("id") is q
        assert q.having("COUNT(*) > 1") is q


class TestSelectWithJoins:
    """Test the select_with_joins convenience method."""

    def test_select_with_joins_basic(self):
        q = QueryBuilder()
        result = q.select_with_joins(
            tables=["users", "orders"],
            columns=["users.id", "orders.total"],
            conditions=["users.id = orders.user_id"],
        )
        assert "FROM users" in result
        assert "INNER JOIN orders ON users.id = orders.user_id" in result
        assert "SELECT users.id, orders.total" in result

    def test_select_with_joins_no_conditions(self):
        q = QueryBuilder()
        result = q.select_with_joins(
            tables=["users", "orders"],
            columns=["users.id"],
        )
        assert "FROM users" in result
        assert "JOIN" not in result


class TestBuildAggregationQuery:
    """Test the build_aggregation_query helper."""

    def test_sum_aggregation(self):
        result = build_aggregation_query("orders", "user_id", "total", "SUM")
        assert "SUM(total)" in result
        assert "GROUP BY user_id" in result

    def test_avg_aggregation(self):
        result = build_aggregation_query("products", "category", "price", "AVG")
        assert "AVG(price)" in result

    def test_count_aggregation(self):
        result = build_aggregation_query("logs", "level", "id", "COUNT")
        assert "COUNT(id)" in result


class TestBuildWindowQuery:
    """Test the build_window_query helper."""

    def test_row_number_window(self):
        result = build_window_query("employees", "dept", "salary")
        assert "ROW_NUMBER()" in result
        assert "PARTITION BY dept" in result
        assert "ORDER BY salary" in result

    def test_rank_window(self):
        result = build_window_query("scores", "subject", "points", "RANK")
        assert "RANK()" in result
        assert "PARTITION BY subject" in result

    def test_dense_rank_window(self):
        result = build_window_query("products", "category", "price", "DENSE_RANK")
        assert "DENSE_RANK()" in result
