"""
Summary Service - Generate brief summaries of PDF content
"""
import os
from langchain_openai import ChatOpenAI


async def generate_pdf_summary(pdf_text: str, filename: str) -> str:
    """
    Generate a concise summary of PDF content using LLM

    Args:
        pdf_text: Extracted PDF text
        filename: PDF filename for context

    Returns:
        Brief summary (2-3 sentences)
    """
    model = ChatOpenAI(
        model="gpt-4o-mini",  # Cheaper model for summaries
        temperature=0.3,
        openai_api_key=os.getenv("OPENAI_API_KEY")
    )

    # Use first 3000 characters for summary (avoid token limits)
    preview_text = pdf_text[:3000]

    prompt = f"""Analyze this financial document and provide a very brief 2-3 sentence summary.
Focus on: company name, document type (annual report, investor presentation, etc.), key financial metrics or time period if mentioned.

Document: {filename}

Content preview:
{preview_text}

Summary (2-3 sentences max):"""

    try:
        response = await model.ainvoke([{"role": "user", "content": prompt}])
        summary = response.content.strip()

        # Limit to 200 characters max
        if len(summary) > 200:
            summary = summary[:197] + "..."

        return summary

    except Exception as e:
        print(f"Summary generation error: {e}")
        return "Financial document - summary unavailable"
