"""
Chat Service - Conversational AI for DCF model analysis
"""
import os
import json
from typing import Dict, Any, List
from langchain_openai import ChatOpenAI


async def chat_with_model(
    message: str,
    model_data: Dict[str, Any],
    history: List[Dict[str, str]] = None
) -> str:
    """
    Chat with the DCF model using conversational AI

    Args:
        message: User's question
        model_data: Current DCF model data
        history: Conversation history

    Returns:
        AI response as string
    """
    if history is None:
        history = []

    model = ChatOpenAI(
        model="gpt-4-turbo-preview",
        temperature=0.7,
        openai_api_key=os.getenv("OPENAI_API_KEY")
    )

    # Build context from model data
    model_context = build_model_context(model_data)

    # Build conversation history
    conversation_history = "\n".join([
        f"{'User' if h.get('role') == 'user' else 'Assistant'}: {h.get('content')}"
        for h in history
    ])

    prompt = f"""You are a financial analysis assistant helping analyze a DCF model.

Current DCF Model Summary:
{model_context}

Previous Conversation:
{conversation_history}

User Question: {message}

Provide a clear, insightful answer. If the question involves "what if" scenarios or sensitivity analysis,
explain how changes would flow through the model. Be specific and reference actual values from the model when relevant."""

    try:
        response = await model.ainvoke([{"role": "user", "content": prompt}])
        return response.content
    except Exception as e:
        print(f"Chat error: {e}")
        raise Exception("Failed to generate chat response")


def build_model_context(model_data: Dict[str, Any]) -> str:
    """
    Build a textual summary of the model for context
    """
    context = ""

    # Extract key metrics from each sheet
    for sheet_name, sheet in model_data.items():
        values = sheet.get("values", [])

        if values:
            context += f"\n{sheet_name}:\n"

            # Include first few rows for context
            preview_rows = values[:10]
            preview = "\n".join([" | ".join(map(str, row)) for row in preview_rows])
            context += preview + "\n"

    # Limit context size
    return context[:3000]


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
