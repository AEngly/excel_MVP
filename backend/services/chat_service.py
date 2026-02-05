"""
Chat Service - Conversational AI for DCF model analysis
"""
import os
import json
from typing import Dict, Any, List, Optional
from langchain_openai import ChatOpenAI
from services.embedding_service import search_chunks


async def chat_with_model(
    message: str,
    model_data: Dict[str, Any],
    history: List[Dict[str, str]] = None,
    pdf_context: Optional[Dict[str, Any]] = None,
    agent_mode: bool = False
) -> str:
    """
    Chat with the DCF model using conversational AI

    Args:
        message: User's question
        model_data: Current DCF model data (optional - empty dict if not provided)
        history: Conversation history
        pdf_context: Optional dict with PDF chunks and embeddings for semantic search
        agent_mode: True = can read and write Excel, False = read-only

    Returns:
        AI response as JSON string with structure: {"response": "...", "actions": [...]}
    """
    if history is None:
        history = []

    model = ChatOpenAI(
        model="gpt-4-turbo-preview",
        temperature=0.7,
        openai_api_key=os.getenv("OPENAI_API_KEY")
    )

    # Build conversation history
    conversation_history = "\n".join([
        f"{'User' if h.get('role') == 'user' else 'Assistant'}: {h.get('content')}"
        for h in history
    ])

    # Search PDF for relevant context if available
    pdf_context_text = ""
    if pdf_context and pdf_context.get("chunks") and pdf_context.get("embeddings"):
        try:
            print(f"🔍 Searching PDF for: {message[:50]}...")
            print(f"📚 Available chunks: {len(pdf_context['chunks'])}")
            print(f"📊 Available embeddings: {len(pdf_context['embeddings'])}")

            relevant_chunks = search_chunks(
                query=message,
                chunks=pdf_context["chunks"],
                embeddings=pdf_context["embeddings"],
                top_k=5  # Increased from 3 to 5 for better coverage
            )

            if relevant_chunks:
                pdf_context_text = "\n\nRelevant PDF Context (use this to answer the question):\n"
                for i, (chunk, score) in enumerate(relevant_chunks, 1):
                    pdf_context_text += f"\n[Excerpt {i}, relevance score: {score:.2f}]\n{chunk}\n"
                    print(f"  📄 Chunk {i}: relevance {score:.3f}, length {len(chunk)} chars")
            else:
                print("⚠️  No relevant chunks found!")
        except Exception as e:
            print(f"⚠️  PDF search error: {e}")
            import traceback
            traceback.print_exc()
            # Continue without PDF context if search fails
    else:
        print("ℹ️  No PDF context available for this query")

    # Build model context if available
    model_context = ""
    if model_data and len(model_data) > 0:
        print(f"📋 Model data keys: {list(model_data.keys())}")
        for sheet_name, sheet_data in model_data.items():
            print(f"  Sheet '{sheet_name}': {list(sheet_data.keys())}")
            if "cells" in sheet_data:
                print(f"    Sparse format: {len(sheet_data['cells'])} cells")
                # Show first few cells for debugging
                for i, cell in enumerate(sheet_data['cells'][:5]):
                    print(f"      Cell {i+1}: row={cell.get('row')}, col={cell.get('col')}, value={cell.get('value')}")

        model_context = "\n\nCurrent Excel Model:\n" + build_model_context(model_data)
        print(f"📊 Excel model context built: {len(model_context)} chars from {len(model_data)} sheets")
        print(f"📝 First 500 chars of context:\n{model_context[:500]}")
    else:
        print("ℹ️  No Excel model data available")

    # If no model_data, just do standard chat (read-only)
    if not model_data or len(model_data) == 0:
        prompt = f"""🌍 CRITICAL LANGUAGE INSTRUCTION:
Detect the language of the user's current message and respond in EXACTLY that language.
- If user writes in English → respond in English
- If user writes in Danish → respond in Danish
- If user writes in Norwegian → respond in Norwegian
IGNORE previous conversation language - match ONLY the current message language.

You are a helpful AI assistant for financial analysis and DCF modeling.
{pdf_context_text}

Previous Conversation:
{conversation_history}

User: {message}

If PDF context is provided above, use it to give specific answers with numbers and citations. If no PDF context is available, provide general helpful guidance on the topic.

Return ONLY a JSON object with this format:
{{
  "response": "Your helpful response in the EXACT SAME LANGUAGE as the user's current message",
  "actions": []
}}

Be helpful and informative regardless of whether PDF context is available."""
    else:
        # Model data available
        if agent_mode:
            # AGENT MODE: Can read AND write
            prompt = f"""🌍 CRITICAL LANGUAGE INSTRUCTION:
Detect the language of the user's current message and respond in EXACTLY that language.
- If user writes in English → respond in English
- If user writes in Danish → respond in Danish
- If user writes in Norwegian → respond in Norwegian
IGNORE previous conversation language - match ONLY the current message language.

You are an Excel AI assistant in AGENT MODE - you can READ and WRITE to Excel.

CURRENT EXCEL MODEL:
{model_context}

{pdf_context_text}

Previous Conversation:
{conversation_history}

User: {message}

🤖 AGENT MODE ACTIVE: You CAN perform actions in Excel.

INSTRUCTIONS:
- When user asks to CREATE/WRITE/ADD content: Generate actions to do it
- When user asks to CLEAR/DELETE/REMOVE: Use clearRange action
- When user asks about existing content: Read from Excel Model context above
- If sheet is empty, that's fine - you can still create content with actions

Return ONLY valid JSON with this structure:
{{
  "response": "Brief explanation in EXACT SAME LANGUAGE as user's current message",
  "actions": [
    {{"type": "setRangeValues", "sheet": "SheetName", "range": "B2:K2", "values": [[100, 200, 300, 400, 500, 600, 700, 800, 900, 1000]]}},
    {{"type": "setFormula", "sheet": "SheetName", "cell": "B3", "formula": "=B2/(1+0.05)^1"}},
    {{"type": "clearRange", "sheet": "SheetName", "range": "A10:A20"}},
    {{"type": "formatCell", "sheet": "SheetName", "cell": "A1", "format": {{"bold": true, "numberFormat": "#,##0"}}}}
  ]
}}

Action types:
- setCellValue: Set a single cell to a number, string, or boolean
- setFormula: Set a single cell formula (must start with =)
- setRangeValues: Set multiple cells at once with 2D array
- setRangeFormulas: Set formulas for multiple cells (use for connected models)
- clearRange: Clear/delete content from a range (use this instead of empty arrays)
- formatCell: Format a cell (bold, numberFormat, bgColor, fontColor)

CRITICAL: For setRangeValues and setRangeFormulas, the array dimensions MUST match the range exactly!

{'🚨 CRITICAL: When user asks to clear/delete/remove cells, you MUST generate clearRange actions! Do not just say it is done - generate the action!' if agent_mode else ''}

⚠️ BEFORE CREATING ANY ACTION WITH YEARS:
1. COUNT THE YEARS: End_Year - Start_Year + 1
   - Example: 2026 to 2040 → 2040 - 2026 + 1 = 15 years
   - Example: 2026 to 2037 → 2037 - 2026 + 1 = 12 years
   - Example: 2025 to 2034 → 2034 - 2025 + 1 = 10 years

2. COUNT YOUR ARRAY: len(values[0]) must equal number of years
   - 15 years = 15 values in array
   - 12 years = 12 values in array

3. CALCULATE END COLUMN:
   - Formula: start_column_number + number_of_years - 1
   - A (col 1) with 15 years: 1 + 15 - 1 = 15 = O
   - D (col 4) with 12 years: 4 + 12 - 1 = 15 = O
   - A (col 1) with 10 years: 1 + 10 - 1 = 10 = J

Column letter to number mapping:
A=1, B=2, C=3, D=4, E=5, F=6, G=7, H=8, I=9, J=10, K=11, L=12, M=13, N=14, O=15, P=16, Q=17, R=18, S=19, T=20

CONCRETE EXAMPLES:
❌ WRONG: Years 2026-2040 = 15 years, range A1:N1 = 14 columns → DIMENSION MISMATCH!
✅ RIGHT: Years 2026-2040 = 15 years, range A1:O1 = 15 columns → CORRECT!

❌ WRONG: Years 2026-2037 = 12 years, range D4:P4 = 13 columns → DIMENSION MISMATCH!
✅ RIGHT: Years 2026-2037 = 12 years, range D4:O4 = 12 columns → CORRECT!

❌ WRONG: Years 2025-2034 = 10 years, range D4:N4 = 11 columns → DIMENSION MISMATCH!
✅ RIGHT: Years 2025-2034 = 10 years, range D4:M4 = 10 columns → CORRECT!

Complex model example - "Create cash flow model with NPV and IRR":
{{
  "response": "I've created a cash flow model with NPV and IRR calculations",
  "actions": [
    {{"type": "setRangeValues", "sheet": "Cash Flow", "range": "A1:F1", "values": [["Year", "2024", "2025", "2026", "2027", "2028"]]}},
    {{"type": "setRangeValues", "sheet": "Cash Flow", "range": "A2:A5", "values": [["Cash Flow"], ["Discount Rate"], ["NPV"], ["IRR"]]}},
    {{"type": "setRangeValues", "sheet": "Cash Flow", "range": "B2:F2", "values": [[-1000, 300, 400, 500, 600]]}},
    {{"type": "setCellValue", "sheet": "Cash Flow", "cell": "B3", "value": 0.1}},
    {{"type": "setFormula", "sheet": "Cash Flow", "cell": "B4", "formula": "=NPV(B3, C2:F2) + B2"}},
    {{"type": "setFormula", "sheet": "Cash Flow", "cell": "B5", "formula": "=IRR(B2:F2)"}},
    {{"type": "formatCell", "sheet": "Cash Flow", "cell": "B3", "format": {{"numberFormat": "0.0%"}}}},
    {{"type": "formatCell", "sheet": "Cash Flow", "cell": "B5", "format": {{"numberFormat": "0.00%"}}}}
  ]
}}

Build interconnected models where formulas reference other cells. Use Excel functions: SUM, NPV, IRR, XNPV, PMT, etc."""
        else:
            # READ-ONLY MODE: Can only read
            prompt = f"""🌍 CRITICAL LANGUAGE INSTRUCTION:
Detect the language of the user's current message and respond in EXACTLY that language.
- If user writes in English → respond in English
- If user writes in Danish → respond in Danish
- If user writes in Norwegian → respond in Norwegian
IGNORE previous conversation language - match ONLY the current message language.

You are an Excel AI assistant in READ-ONLY MODE - you can only READ Excel, not write.

CURRENT EXCEL MODEL:
{model_context}

{pdf_context_text}

Previous Conversation:
{conversation_history}

User: {message}

📖 READ-ONLY MODE: You CANNOT make changes to Excel.

INSTRUCTIONS:
- Answer questions about existing content in the Excel Model above
- If user asks to CREATE/WRITE/CHANGE anything, inform them to enable Agent Mode
- If a cell is listed in Excel Model, it HAS content - answer based on what you see
- If a cell is NOT listed, it is empty
- Always return empty actions array in read-only mode

Return ONLY valid JSON:
{{
  "response": "Your answer in EXACT SAME LANGUAGE as user's current message (if user asks for changes, tell them to enable Agent Mode)",
  "actions": []
}}"""

    try:
        response = await model.ainvoke([{"role": "user", "content": prompt}])
        # Return the raw JSON string - frontend will parse it
        return response.content
    except Exception as e:
        print(f"Chat error: {e}")
        # Return error as valid JSON
        return json.dumps({
            "response": f"Error: {str(e)}",
            "actions": []
        })


def build_model_context(model_data: Dict[str, Any]) -> str:
    """
    Build a textual summary of the model for context with cell references
    Supports both old format (values/formulas arrays) and new sparse format (cells array)
    """
    def col_letter(col_num):
        """Convert column number to letter (1=A, 2=B, etc.)"""
        letters = ""
        while col_num > 0:
            col_num, remainder = divmod(col_num - 1, 26)
            letters = chr(65 + remainder) + letters
        return letters

    context = ""

    # Extract key metrics from each sheet
    for sheet_name, sheet in model_data.items():
        context += f"\n=== Sheet: {sheet_name} ===\n"

        # Check if using new sparse format
        if "cells" in sheet:
            # New format - array of non-empty cells
            cells = sheet["cells"]
            print(f"  📊 Sparse format: {len(cells)} non-empty cells")

            for cell in cells[:100]:  # Limit to first 100 cells
                col_letter_str = col_letter(cell["col"] + 1)
                row_num = cell["row"] + 1
                cell_ref = f"{col_letter_str}{row_num}"

                # Build cell description - OPTIMIZED for token efficiency
                cell_desc = f"{cell_ref}: "

                # Show formula OR value (not both to save tokens)
                if cell.get("formula"):
                    # If formula exists, only show formula and final value if different
                    formula_str = cell['formula']
                    if str(cell['value']) != formula_str:  # Only show value if different from formula
                        cell_desc += f"{formula_str} = {cell['value']}"
                    else:
                        cell_desc += formula_str
                else:
                    # No formula, just value
                    cell_desc += str(cell['value'])

                # Add number format ONLY if not General (save tokens)
                if cell.get("numberFormat") and cell["numberFormat"] != "General":
                    cell_desc += f" [{cell['numberFormat']}]"

                # Add formatting ONLY if present (skip defaults)
                if cell.get("bold"):
                    cell_desc += " [bold]"

                context += cell_desc + "\n"

        else:
            # Old format - full arrays (for backward compatibility)
            values = sheet.get("values", [])
            formulas = sheet.get("formulas", [])
            number_format = sheet.get("numberFormat", [])
            formatting = sheet.get("formatting", [])

            if values:
                # Show data with cell references
                max_rows = min(20, len(values))
                max_cols = min(20, len(values[0]) if values else 0)

                for row_idx in range(max_rows):
                    row_num = row_idx + 1
                    row_data = values[row_idx]

                    for col_idx in range(min(max_cols, len(row_data))):
                        col_letter_str = col_letter(col_idx + 1)
                        cell_ref = f"{col_letter_str}{row_num}"
                        value = row_data[col_idx]

                        # Skip empty cells
                        if value == "" or value is None:
                            continue

                        # Build cell description
                        cell_desc = f"{cell_ref}: "

                        # Show formula if available
                        if formulas and row_idx < len(formulas) and col_idx < len(formulas[row_idx]):
                            formula = formulas[row_idx][col_idx]
                            if formula and formula != "":
                                cell_desc += f"{formula} (displays as: {value})"
                            else:
                                cell_desc += f"{value}"
                        else:
                            cell_desc += f"{value}"

                        # Add number format if not General
                        if number_format and row_idx < len(number_format) and col_idx < len(number_format[row_idx]):
                            num_fmt = number_format[row_idx][col_idx]
                            if num_fmt and num_fmt != "General":
                                cell_desc += f" [format: {num_fmt}]"

                        # Add formatting if present
                        if formatting and row_idx < len(formatting) and col_idx < len(formatting[row_idx]):
                            fmt = formatting[row_idx][col_idx]
                            fmt_details = []
                            if fmt.get("bold"):
                                fmt_details.append("bold")
                            if fmt.get("fontColor") and fmt["fontColor"] != "#000000":
                                fmt_details.append(f"color:{fmt['fontColor']}")
                            if fmt.get("fillColor") and fmt["fillColor"] != "#FFFFFF":
                                fmt_details.append(f"bg:{fmt['fillColor']}")
                            if fmt_details:
                                cell_desc += f" [{', '.join(fmt_details)}]"

                        context += cell_desc + "\n"

    # Limit context size
    return context[:8000]


async def run_sensitivity_analysis(
    model_data: Dict[str, Any],
    variable: str,
    range_values: str
) -> str:
    """
    Run sensitivity analysis on a variable

    Args:
        model_data: DCF model data
        variable: Variable to analyze
        range_values: Range of values to test

    Returns:
        Analysis explanation
    """
    model = ChatOpenAI(
        model="gpt-4-turbo-preview",
        temperature=0.5,
        openai_api_key=os.getenv("OPENAI_API_KEY")
    )

    model_context = build_model_context(model_data)[:2000]

    prompt = f"""Given this DCF model, explain how changing {variable} across the range {range_values}
would impact the enterprise value and equity value. Provide specific directional and magnitude insights.

Model context:
{model_context}"""

    response = await model.ainvoke([{"role": "user", "content": prompt}])
    return response.content
