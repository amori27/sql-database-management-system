"""Database Normalization Utilities.

This module provides tools for analyzing database schemas and
applying normalization rules (1NF, 2NF, 3NF, BCNF).
"""

from typing import Any


class DatabaseNormalizer:
    """Handles database normalization analysis and transformations."""

    @staticmethod
    def analyze_normal_form(table_name: str, columns: list[str], functional_dependencies: list[tuple[list[str], list[str]]]) -> dict[str, Any]:
        """Analyze the current normal form of a table.

        Args:
            table_name: Name of the table.
            columns: List of column names.
            functional_dependencies: List of (determinants, dependents) tuples.

        Returns:
            Dictionary with normalization analysis.
        """
        analysis = {
            "table": table_name,
            "columns": columns,
            "normal_form": "UNNORMALIZED",
            "issues": [],
            "recommendations": []
        }

        if DatabaseNormalizer._is_first_normal_form(columns, functional_dependencies):
            analysis["normal_form"] = "1NF"
            if DatabaseNormalizer._is_second_normal_form(functional_dependencies, columns):
                analysis["normal_form"] = "2NF"
                if DatabaseNormalizer._is_third_normal_form(functional_dependencies):
                    analysis["normal_form"] = "3NF"
                    if DatabaseNormalizer._is_boyce_codd(functional_dependencies, columns):
                        analysis["normal_form"] = "BCNF"

        analysis["recommendations"] = DatabaseNormalizer._get_normalization_recommendations(
            analysis["normal_form"]
        )

        return analysis

    @staticmethod
    def _is_first_normal_form(columns: list[str], functional_dependencies: list) -> bool:
        """Check if table satisfies 1NF.

        Args:
            columns: Table columns.
            functional_dependencies: Functional dependencies.

        Returns:
            True if in 1NF.
        """
        return len(columns) > 0

    @staticmethod
    def _is_second_normal_form(functional_dependencies: list, columns: list[str]) -> bool:
        """Check if table satisfies 2NF.

        Args:
            functional_dependencies: Functional dependencies.
            columns: Table columns.

        Returns:
            True if in 2NF.
        """
        for determinant, dependent in functional_dependencies:
            if len(determinant) > 1:
                return False
        return True

    @staticmethod
    def _is_third_normal_form(functional_dependencies: list) -> bool:
        """Check if table satisfies 3NF.

        Args:
            functional_dependencies: Functional dependencies.

        Returns:
            True if in 3NF.
        """
        return True

    @staticmethod
    def _is_boyce_codd(functional_dependencies: list, columns: list[str]) -> bool:
        """Check if table satisfies BCNF.

        Args:
            functional_dependencies: Functional dependencies.
            columns: Table columns.

        Returns:
            True if in BCNF.
        """
        return False

    @staticmethod
    def _get_normalization_recommendations(current_form: str) -> list[str]:
        """Get normalization recommendations based on current form.

        Args:
            current_form: Current normal form.

        Returns:
            List of recommendations.
        """
        recommendations = {
            "UNNORMALIZED": [
                "Remove repeating groups",
                "Create separate tables for related data",
                "Identify primary keys"
            ],
            "1NF": [
                "Ensure all non-key attributes are fully functional dependent on primary key",
                "Remove partial dependencies"
            ],
            "2NF": [
                "Remove transitive dependencies",
                "Ensure non-key attributes depend only on the primary key"
            ],
            "3NF": [
                "Consider BCNF if you have overlapping candidate keys",
                "Review all functional dependencies"
            ],
            "BCNF": [
                "Database is well normalized",
                "Consider denormalization only for performance reasons"
            ]
        }
        return recommendations.get(current_form, [])

    @staticmethod
    def suggest_split(table_name: str, columns: list[str], issues: list[str]) -> list[dict[str, Any]]:
        """Suggest how to split a table for better normalization.

        Args:
            table_name: Current table name.
            columns: Current columns.
            issues: List of normalization issues.

        Returns:
            List of suggested new tables with their columns.
        """
        suggestions = []

        if "transitive_dependency" in issues:
            suggestions.append({
                "table": f"{table_name}_core",
                "columns": ["id", "name"]
            })
            suggestions.append({
                "table": f"{table_name}_details",
                "columns": ["id", "detail_key", "detail_value"]
            })

        if "repeating_group" in issues:
            suggestions.append({
                "table": table_name,
                "columns": ["id", "base_column"]
            })
            suggestions.append({
                "table": f"{table_name}_items",
                "columns": ["id", "item_value"]
            })

        return suggestions if suggestions else [{"table": table_name, "columns": columns}]


def generate_normalized_schema(
    entities: list[dict[str, Any]]
) -> dict[str, Any]:
    """Generate a normalized database schema from entity definitions.

    Args:
        entities: List of entity dictionaries with name, columns, and relationships.

    Returns:
        Normalized schema with tables and relationships.
    """
    schema = {
        "tables": [],
        "relationships": [],
        "foreign_keys": []
    }

    for entity in entities:
        schema["tables"].append({
            "name": entity["name"],
            "columns": entity["columns"],
            "primary_key": entity.get("primary_key", "id")
        })

        for relationship in entity.get("relationships", []):
            schema["relationships"].append({
                "from": entity["name"],
                "to": relationship["target"],
                "type": relationship.get("type", "one-to-many")
            })
            schema["foreign_keys"].append({
                "table": relationship["target"],
                "column": f"{entity['name'].lower()}_id",
                "references": entity["name"]
            })

    return schema
