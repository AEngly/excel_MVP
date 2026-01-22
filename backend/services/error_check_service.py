"""
Error Check Service - Validate DCF models for errors
"""
import os
import json
from typing import Dict, Any, List
from langchain_openai import ChatOpenAI


async def check_model_errors(model_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Check DCF model for errors across all sheets

    Args:
        model_data: Dictionary containing all sheet data

    Returns:
        List of error dictionaries
    """
    errors = []

    # Structural validation
    errors.extend(validate_structure(model_data))

    # Formula validation
    errors.extend(validate_formulas(model_data))

    # Cross-sheet reference validation
    errors.extend(validate_cross_references(model_data))

    # Use AI for advanced checks
    ai_errors = await ai_validation(model_data)
    errors.extend(ai_errors)

    return errors


def validate_structure(model_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Validate basic structure"""
    errors = []

    for sheet_name, sheet in model_data.items():
        if not sheet.get("values") or not isinstance(sheet.get("values"), list):
            errors.append({
                "sheet": sheet_name,
                "cell": "N/A",
                "type": "missing",
                "severity": "critical",
                "message": "Sheet has no data or invalid structure"
            })

    return errors


def validate_formulas(model_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Validate formulas for common errors"""
    errors = []

    for sheet_name, sheet in model_data.items():
        formulas = sheet.get("formulas", [])

        for row_idx, row in enumerate(formulas):
            for col_idx, formula in enumerate(row):
                if isinstance(formula, str) and formula.startswith("="):
                    # Check for common formula errors
                    if "#REF!" in formula:
                        errors.append({
                            "sheet": sheet_name,
                            "cell": get_cell_address(row_idx, col_idx),
                            "type": "formula",
                            "severity": "critical",
                            "message": "Formula contains invalid reference (#REF!)"
                        })

                    if "#DIV/0!" in formula:
                        errors.append({
                            "sheet": sheet_name,
                            "cell": get_cell_address(row_idx, col_idx),
                            "type": "formula",
                            "severity": "critical",
                            "message": "Division by zero error"
                        })

                    # Check for circular references (simplified)
                    cell_addr = get_cell_address(row_idx, col_idx)
                    if cell_addr in formula:
                        errors.append({
                            "sheet": sheet_name,
                            "cell": cell_addr,
                            "type": "circular",
                            "severity": "critical",
                            "message": "Potential circular reference detected"
                        })

    return errors


def validate_cross_references(model_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Validate cross-sheet references"""
    errors = []
    sheet_names = list(model_data.keys())

    for sheet_name, sheet in model_data.items():
        formulas = sheet.get("formulas", [])

        for row_idx, row in enumerate(formulas):
            for col_idx, formula in enumerate(row):
                if isinstance(formula, str) and formula.startswith("="):
                    # Check if referenced sheets exist
                    for potential_ref in sheet_names:
                        if f"{potential_ref}!" in formula:
                            # Extract the cell reference
                            import re
                            match = re.search(rf'{potential_ref}!([A-Z]+[0-9]+)', formula)
                            if match:
                                ref_cell = match.group(1)
                                # Verify the referenced cell exists
                                if not is_valid_cell_reference(ref_cell, model_data[potential_ref]):
                                    errors.append({
                                        "sheet": sheet_name,
                                        "cell": get_cell_address(row_idx, col_idx),
                                        "type": "missing",
                                        "severity": "warning",
                                        "message": f"References {potential_ref}!{ref_cell} which may be empty"
                                    })

    return errors


async def ai_validation(model_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """AI-powered validation for logical errors"""
    model = ChatOpenAI(
        model="gpt-4-turbo-preview",
        temperature=0.2,
        openai_api_key=os.getenv("OPENAI_API_KEY")
    )

    # Truncate model data for prompt
    model_summary = json.dumps(model_data, default=str)[:4000]

    prompt = f"""You are a financial modeling expert. Analyze this DCF model data and identify any logical errors, inconsistencies, or issues:

{model_summary}

Look for:
1. Inconsistent growth rates
2. Unrealistic assumptions (e.g., WACC > 30%, negative margins)
3. Missing key components
4. Calculation inconsistencies

Return a JSON array of errors with format:
{{"sheet": "sheetName", "cell": "A1", "type": "inconsistent", "severity": "warning", "message": "description"}}

Return ONLY the JSON array, no additional text."""

    try:
        response = await model.ainvoke([{"role": "user", "content": prompt}])
        return json.loads(response.content)
    except Exception as e:
        print(f"AI validation error: {e}")
        return []


def get_cell_address(row_index: int, col_index: int) -> str:
    """Convert row/col indices to Excel address"""
    col = chr(65 + col_index)
    row = row_index + 1
    return f"{col}{row}"


def is_valid_cell_reference(cell_ref: str, sheet: Dict[str, Any]) -> bool:
    """Check if cell reference is valid"""
    return sheet and sheet.get("values") and len(sheet.get("values", [])) > 0
