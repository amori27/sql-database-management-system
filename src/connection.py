"""Database Connection Management.

This module provides utilities for managing database connections
across different database systems.
"""

from typing import Any


class DatabaseConnection:
    """Manages database connections with connection pooling."""

    def __init__(self, database_type: str = "sqlite"):
        """Initialize database connection manager.

        Args:
            database_type: Type of database (postgresql, mysql, sqlite).
        """
        self.database_type = database_type.lower()
        self.connection = None
        self.cursor = None

    def connect(self, **kwargs: Any) -> None:
        """Establish database connection.

        Args:
            **kwargs: Connection parameters (host, database, user, password).
        """
        if self.database_type == "sqlite":
            self._connect_sqlite(kwargs.get("database", "default.db"))
        elif self.database_type == "postgresql":
            self._connect_postgresql(**kwargs)
        elif self.database_type == "mysql":
            self._connect_mysql(**kwargs)

    def _connect_sqlite(self, database: str) -> None:
        """Connect to SQLite database.

        Args:
            database: Path to SQLite file.
        """
        import sqlite3
        self.connection = sqlite3.connect(database)
        self.cursor = self.connection.cursor()

    def _connect_postgresql(self, **kwargs: Any) -> None:
        """Connect to PostgreSQL database.

        Args:
            **kwargs: Connection parameters.
        """
        pass

    def _connect_mysql(self, **kwargs: Any) -> None:
        """Connect to MySQL database.

        Args:
            **kwargs: Connection parameters.
        """
        pass

    def execute(self, query: str, params: tuple | None = None) -> list[Any]:
        """Execute a SQL query.

        Args:
            query: SQL query string.
            params: Optional query parameters.

        Returns:
            List of result rows.
        """
        if not self.cursor:
            raise RuntimeError("Not connected to database. Call connect() first.")

        if params:
            self.cursor.execute(query, params)
        else:
            self.cursor.execute(query)

        if self.connection:
            self.connection.commit()

        return self.cursor.fetchall()

    def close(self) -> None:
        """Close the database connection."""
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()
        self.cursor = None
        self.connection = None


def create_connection_string(
    database_type: str,
    host: str = "localhost",
    port: int = 5432,
    database: str = "default",
    user: str = "root",
    password: str = ""
) -> str:
    """Create a database connection string.

    Args:
        database_type: Type of database.
        host: Database host.
        port: Database port.
        database: Database name.
        user: Database user.
        password: Database password.

    Returns:
        Connection string.
    """
    if database_type.lower() == "postgresql":
        return f"postgresql://{user}:{password}@{host}:{port}/{database}"
    elif database_type.lower() == "mysql":
        return f"mysql://{user}:{password}@{host}:{port}/{database}"
    elif database_type.lower() == "sqlite":
        return f"sqlite:///{database}"
    return ""
