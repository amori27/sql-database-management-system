# SQL Database Management

PostgreSQL/MySQL/SQLite utilities: a query builder for JOINs and aggregations, query optimizer that runs EXPLAIN and suggests indexes, schema normalizer (1NF–BCNF), and DB connection pooler.

## Usage

```python
from src.query_builder import QueryBuilder
qb = QueryBuilder()
result = qb.select_with_joins(
    tables=['users', 'orders'],
    columns=['users.name', 'orders.total'],
    conditions=['users.id = orders.user_id']
)
```

```python
from src.optimizer import QueryOptimizer
optimizer = QueryOptimizer()
optimized_query = optimizer.analyze_and_optimize(
    "SELECT * FROM orders WHERE date > '2024-01-01'"
)
```

## License

MIT
