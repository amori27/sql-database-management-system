# SQL Database Management System
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)


A comprehensive SQL toolkit featuring complex queries, performance optimization techniques, database normalization patterns, and advanced SQL functions for modern data management.

## Description

This project provides production-ready SQL scripts and Python utilities for database management, including query optimization, schema normalization, and complex data manipulations across PostgreSQL, MySQL, and SQLite.

## Skills & Technologies

- SQL (PostgreSQL, MySQL, SQLite)
- Database Normalization (1NF, 2NF, 3NF, BCNF)
- Query Optimization & Indexing
- Python DB-API / SQLAlchemy
- Stored Procedures & Triggers
- Transaction Management

## Installation

```bash
git clone https://github.com/amori27/sql-database-management-system.git
cd sql-database-management-system
pip install -r requirements.txt
```

## Usage

### Complex Queries

```python
from src.query_builder import QueryBuilder

qb = QueryBuilder()
result = qb.select_with_joins(
    tables=['users', 'orders'],
    columns=['users.name', 'orders.total'],
    conditions=['users.id = orders.user_id']
)
```

### Performance Optimization

```python
from src.optimizer import QueryOptimizer

optimizer = QueryOptimizer()
optimized_query = optimizer.analyze_and_optimize(
    "SELECT * FROM orders WHERE date > '2024-01-01'"
)
```

## Project Structure

```
sql-database-management-system/
├── src/
│   ├── __init__.py
│   ├── query_builder.py       # Query construction utilities
│   ├── optimizer.py            # Query optimization
│   ├── normalizer.py           # Database normalization
│   └── connection.py           # Database connections
├── sql/
│   ├── schema.sql              # Database schema
│   └── queries.sql             # Example queries
├── tests/
├── requirements.txt
└── README.md
```

## References

- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [SQL Style Guide](https://www.sqlstyle.guide/)
- [Database Normalization Forms](https://www.bcnf.info/)

## License

MIT License
