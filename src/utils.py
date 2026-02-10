"""
Utility functions for the Project Cost Analyzer.
"""

from typing import Dict, List
import os


def validate_positive_number(value: float, field_name: str) -> None:
    """
    Validate that a number is positive.

    Args:
        value: The number to validate
        field_name: Name of the field for error messages

    Raises:
        ValueError: If value is not positive
    """
    if value <= 0:
        raise ValueError(f"{field_name} must be a positive number. Got: {value}")


def validate_risk_level(risk_level: str) -> str:
    """
    Validate and normalize risk level input.

    Args:
        risk_level: Risk level string (low, medium, high)

    Returns:
        Normalized risk level in lowercase

    Raises:
        ValueError: If risk level is invalid
    """
    risk_level = risk_level.lower().strip()
    valid_levels = ['low', 'medium', 'high']

    if risk_level not in valid_levels:
        raise ValueError(
            f"Risk level must be one of {valid_levels}. Got: {risk_level}"
        )

    return risk_level


def get_risk_multiplier(risk_level: str) -> float:
    """
    Get the cost/time multiplier for a given risk level.

    Args:
        risk_level: Risk level (low, medium, high)

    Returns:
        Multiplier value
    """
    multipliers = {
        'low': 1.1,  # 10% overhead
        'medium': 1.3,  # 30% overhead
        'high': 1.6  # 60% overhead
    }
    return multipliers.get(risk_level.lower(), 1.3)


def format_currency(amount: float) -> str:
    """
    Format a number as currency (USD).

    Args:
        amount: The amount to format

    Returns:
        Formatted currency string
    """
    return f"${amount:,.2f}"


def format_duration(days: float) -> str:
    """
    Format duration in days as a readable string.

    Args:
        days: Number of days

    Returns:
        Formatted duration string
    """
    if days < 1:
        return f"{days:.1f} days"
    elif days == 1:
        return "1 day"
    else:
        weeks = days / 5  # Work weeks
        if weeks >= 1:
            return f"{days:.1f} days ({weeks:.1f} weeks)"
        return f"{days:.1f} days"


def ensure_output_directory(directory: str = "output/reports") -> str:
    """
    Ensure the output directory exists.

    Args:
        directory: Path to the output directory

    Returns:
        Absolute path to the directory
    """
    os.makedirs(directory, exist_ok=True)
    return os.path.abspath(directory)


def calculate_percentile(values: List[float], percentile: float) -> float:
    """
    Calculate a percentile from a list of values.

    Args:
        values: List of numeric values
        percentile: Percentile to calculate (0-100)

    Returns:
        The percentile value
    """
    if not values:
        return 0.0

    sorted_values = sorted(values)
    index = int(len(sorted_values) * (percentile / 100))
    index = min(index, len(sorted_values) - 1)

    return sorted_values[index]


def print_section_header(title: str, width: int = 60) -> None:
    """
    Print a formatted section header.

    Args:
        title: Header title
        width: Total width of the header
    """
    print("\n" + "=" * width)
    print(f"  {title}")
    print("=" * width)


def print_key_value(key: str, value: str, indent: int = 2) -> None:
    """
    Print a key-value pair with formatting.

    Args:
        key: The key/label
        value: The value
        indent: Number of spaces to indent
    """
    spaces = " " * indent
    print(f"{spaces}{key}: {value}")


def save_text_report(content: str, filename: str, directory: str = "output/reports") -> str:
    """
    Save a text report to a file.

    Args:
        content: The text content to save
        filename: Name of the file
        directory: Directory to save in

    Returns:
        Full path to the saved file
    """
    ensure_output_directory(directory)
    filepath = os.path.join(directory, filename)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

    return filepath