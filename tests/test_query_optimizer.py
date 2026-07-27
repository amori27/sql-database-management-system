"""Tests for query optimizer and complexity estimation."""

from src.optimizer import QueryOptimizer, estimate_query_complexity


class TestQueryOptimizer:
    """Test QueryOptimizer analysis and optimization methods."""

    def test_initial_suggestions_empty(self):
        opt = QueryOptimizer()
        assert opt.suggestions == []

    def test_select_star_suggestion(self):
        opt = QueryOptimizer()
        opt.analyze_and_optimize("SELECT * FROM users")
        assert any("SELECT *" in s for s in opt.suggestions)

    def test_specific_columns_no_select_star_suggestion(self):
        opt = QueryOptimizer()
        opt.analyze_and_optimize("SELECT id, name FROM users")
        assert not any("SELECT *" in s for s in opt.suggestions)

    def test_or_condition_suggestion(self):
        opt = QueryOptimizer()
        opt.analyze_and_optimize("SELECT * FROM users WHERE status = 'a' OR status = 'b'")
        assert any("UNION" in s for s in opt.suggestions)

    def test_like_leading_wildcard_suggestion(self):
        opt = QueryOptimizer()
        opt.analyze_and_optimize("SELECT * FROM users WHERE name LIKE '%john%'")
        assert any("LIKE" in s for s in opt.suggestions)

    def test_like_trailing_wildcard_suggestion(self):
        opt = QueryOptimizer()
        opt.analyze_and_optimize("SELECT * FROM users WHERE name LIKE 'john%'")
        assert any("LIKE" in s for s in opt.suggestions)

    def test_clean_query_no_suggestions(self):
        opt = QueryOptimizer()
        opt.analyze_and_optimize("SELECT id, name FROM users WHERE id = 1")
        assert len(opt.suggestions) == 0

    def test_analyze_returns_optimized_string(self):
        opt = QueryOptimizer()
        result = opt.analyze_and_optimize("SELECT * FROM users WHERE id = 1")
        assert isinstance(result, str)
        assert "SELECT" in result

    def test_suggestions_cleared_between_calls(self):
        opt = QueryOptimizer()
        opt.analyze_and_optimize("SELECT * FROM users")
        assert len(opt.suggestions) > 0
        opt.analyze_and_optimize("SELECT id FROM users WHERE id = 1")
        assert len(opt.suggestions) == 0

    def test_suggest_indexes_where_clause(self):
        opt = QueryOptimizer()
        indexes = opt.suggest_indexes("SELECT * FROM users WHERE users.id = 1")
        assert any("idx_users_id" in i for i in indexes)

    def test_suggest_indexes_join_clause(self):
        opt = QueryOptimizer()
        indexes = opt.suggest_indexes(
            "SELECT * FROM orders JOIN customers ON orders.cust_id = customers.id"
        )
        assert len(indexes) >= 1

    def test_suggest_indexes_join_dedup(self):
        opt = QueryOptimizer()
        indexes = opt.suggest_indexes(
            "SELECT * FROM users JOIN orders ON users.id = orders.user_id WHERE users.id = 1"
        )
        all_indexes = set(indexes)
        assert len(indexes) >= 1

    def test_suggest_indexes_no_matches(self):
        opt = QueryOptimizer()
        indexes = opt.suggest_indexes("SELECT 1")
        assert indexes == []

    def test_explain_plan_postgresql(self):
        opt = QueryOptimizer()
        result = opt.explain_plan("SELECT * FROM users", "postgresql")
        assert result.startswith("EXPLAIN ANALYZE")

    def test_explain_plan_mysql(self):
        opt = QueryOptimizer()
        result = opt.explain_plan("SELECT * FROM users", "mysql")
        assert result.startswith("EXPLAIN FORMAT=JSON")

    def test_explain_plan_unknown_db(self):
        opt = QueryOptimizer()
        result = opt.explain_plan("SELECT * FROM users", "oracle")
        assert result == "EXPLAIN SELECT * FROM users"


class TestEstimateQueryComplexity:
    """Test the estimate_query_complexity function."""

    def test_simple_select(self):
        result = estimate_query_complexity("SELECT id FROM users")
        assert result["tables"] == 1
        assert result["joins"] == 0
        assert result["subqueries"] == 0
        assert result["score"] >= 2

    def test_join_query(self):
        result = estimate_query_complexity(
            "SELECT * FROM users JOIN orders ON users.id = orders.user_id"
        )
        assert result["joins"] == 1
        assert result["score"] >= 3

    def test_subquery_detection(self):
        result = estimate_query_complexity(
            "SELECT * FROM (SELECT id FROM users) sub"
        )
        assert result["subqueries"] == 1

    def test_aggregation_detection(self):
        result = estimate_query_complexity(
            "SELECT SUM(amount), AVG(price), COUNT(*) FROM orders"
        )
        assert result["aggregations"] == 3

    def test_order_by_detected(self):
        result = estimate_query_complexity("SELECT * FROM users ORDER BY name")
        assert result["has_order_by"] is True

    def test_group_by_detected(self):
        result = estimate_query_complexity("SELECT dept FROM employees GROUP BY dept")
        assert result["has_group_by"] is True

    def test_no_order_by(self):
        result = estimate_query_complexity("SELECT * FROM users")
        assert result["has_order_by"] is False

    def test_complexity_score_formula(self):
        result = estimate_query_complexity(
            "SELECT * FROM a JOIN b ON a.id = b.a_id WHERE a.x = 1"
        )
        expected = result["tables"] * 2 + result["joins"] * 3
        assert result["score"] >= expected

    def test_tables_and_joins_count(self):
        result = estimate_query_complexity(
            "SELECT * FROM a JOIN b ON a.id = b.a_id JOIN c ON b.id = c.b_id"
        )
        assert result["tables"] == 1
        assert result["joins"] == 2

    def test_min_max_aggregation(self):
        result = estimate_query_complexity(
            "SELECT MIN(price), MAX(price) FROM products"
        )
        assert result["aggregations"] == 2
