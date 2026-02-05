"""
Action Validator - Validate and fix Excel actions before sending to frontend
"""
import re
from typing import List, Dict, Any


def col_to_num(col: str) -> int:
    """Convert column letter to number (A=1, B=2, etc.)"""
    num = 0
    for char in col:
        num = num * 26 + (ord(char) - 64)
    return num


def validate_range_dimensions(range_str: str, values: List[List[Any]]) -> tuple[bool, str]:
    """
    Validate that values array matches range dimensions

    Args:
        range_str: Excel range like "A1:C3"
        values: 2D array of values

    Returns:
        (is_valid, error_message)
    """
    parts = range_str.split(':')
    if len(parts) != 2:
        return True, ""  # Single cell, no validation needed

    start_cell, end_cell = parts

    # Parse start cell
    start_match = re.match(r'([A-Z]+)(\d+)', start_cell)
    end_match = re.match(r'([A-Z]+)(\d+)', end_cell)

    if not start_match or not end_match:
        return False, f"Invalid range format: {range_str}"

    start_col = start_match.group(1)
    start_row = int(start_match.group(2))
    end_col = end_match.group(1)
    end_row = int(end_match.group(2))

    # Calculate expected dimensions
    expected_rows = end_row - start_row + 1
    expected_cols = col_to_num(end_col) - col_to_num(start_col) + 1

    # Get actual dimensions
    actual_rows = len(values)
    actual_cols = len(values[0]) if values and len(values) > 0 else 0

    if expected_rows != actual_rows or expected_cols != actual_cols:
        return False, f"Range {range_str} expects {expected_rows}x{expected_cols}, but values are {actual_rows}x{actual_cols}"

    return True, ""


def validate_actions(actions: List[Dict[str, Any]]) -> tuple[List[Dict[str, Any]], List[str]]:
    """
    Validate all actions and return validated actions + error messages

    Args:
        actions: List of action dictionaries

    Returns:
        (validated_actions, errors)
    """
    validated = []
    errors = []

    for idx, action in enumerate(actions):
        action_type = action.get('type')

        if action_type == 'setRangeValues':
            range_str = action.get('range')
            values = action.get('values')

            if not range_str or not values:
                errors.append(f"Action {idx+1}: Missing range or values")
                continue

            is_valid, error_msg = validate_range_dimensions(range_str, values)

            if not is_valid:
                errors.append(f"Action {idx+1} ({action_type}): {error_msg}")
                print(f"❌ Validation failed: {error_msg}")
                continue

            print(f"✅ Action {idx+1} validated: {range_str} = {len(values)}x{len(values[0])} ✓")

        elif action_type == 'setRangeFormulas':
            range_str = action.get('range')
            formulas = action.get('formulas')

            if not range_str or not formulas:
                errors.append(f"Action {idx+1}: Missing range or formulas")
                continue

            is_valid, error_msg = validate_range_dimensions(range_str, formulas)

            if not is_valid:
                errors.append(f"Action {idx+1} ({action_type}): {error_msg}")
                print(f"❌ Validation failed: {error_msg}")
                continue

            print(f"✅ Action {idx+1} validated: {range_str} = {len(formulas)}x{len(formulas[0])} ✓")

        # Add validated action
        validated.append(action)

    return validated, errors
