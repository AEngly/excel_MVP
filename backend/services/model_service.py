"""
Model Service - Generate DCF models using LangChain and OpenAI
"""
import os
import json
from typing import Dict, Any
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain


async def generate_dcf_model(pdf_text: str) -> Dict[str, Any]:
    """
    Generate DCF model structure from extracted PDF text

    Args:
        pdf_text: Text extracted from company PDF

    Returns:
        Dictionary with model data (assumptions, financials, dcfCalculations)
    """
    model = ChatOpenAI(
        model="gpt-4-turbo-preview",
        temperature=0.3,
        openai_api_key=os.getenv("OPENAI_API_KEY")
    )

    prompt = PromptTemplate.from_template("""
You are a financial modeling expert. Given the following company information extracted from a PDF,
create a complete DCF (Discounted Cash Flow) model structure.

Extract or reasonably estimate:
1. Historical financials (revenue, EBITDA, CAPEX, working capital changes)
2. Growth assumptions (revenue growth rates, margin assumptions)
3. WACC components (cost of equity, cost of debt, capital structure)
4. Terminal value assumptions

If specific data is missing, make reasonable assumptions based on:
- Industry standards for similar companies
- Context clues from the document
- Conservative financial modeling practices

Return the data as JSON with three sections:
- assumptions: 2D array for Assumptions sheet (labels in col A, values in col B)
- financials: 2D array for Financials sheet (headers in row 1, data below)
- dcfCalculations: 2D array for DCF Calculation sheet (with Excel formulas using = prefix)

Company Information:
{pdf_text}

Return ONLY valid JSON, no additional text.
""")

    chain = LLMChain(llm=model, prompt=prompt)

    try:
        result = await chain.ainvoke({"pdf_text": pdf_text[:8000]})

        # Parse the response
        model_data = json.loads(result["text"])

        # Enhance with research if needed
        if needs_additional_research(model_data):
            model_data = await enhance_with_research(model_data, pdf_text)

        return model_data

    except Exception as e:
        print(f"Model generation error: {e}")
        # Return fallback template if AI fails
        return get_fallback_template()


def needs_additional_research(model_data: Dict[str, Any]) -> bool:
    """Check if model needs additional internet research"""
    return not model_data.get("assumptions") or len(model_data.get("assumptions", [])) < 5


async def enhance_with_research(model_data: Dict[str, Any], pdf_text: str) -> Dict[str, Any]:
    """
    Enhance model data with internet research
    """
    import re

    # Extract company name from PDF text
    company_match = re.search(r'(?:Company|Corporation|Inc|Ltd):\s*([^\n]+)', pdf_text, re.IGNORECASE)
    company_name = company_match.group(1).strip() if company_match else "Unknown Company"

    print(f"🔍 Researching additional data for: {company_name}")

    model = ChatOpenAI(
        model="gpt-4-turbo-preview",
        temperature=0.3,
        openai_api_key=os.getenv("OPENAI_API_KEY")
    )

    research_prompt = f"""Based on general knowledge, provide typical financial metrics for {company_name} or similar companies in the same industry:

- Typical revenue growth rate
- Industry average EBITDA margin
- Typical WACC (discount rate)
- Industry P/E or EV/EBITDA multiples

Return as JSON with keys: revenueGrowth, ebitdaMargin, wacc, terminalMultiple"""

    try:
        response = await model.ainvoke([{"role": "user", "content": research_prompt}])
        research = json.loads(response.content)

        # Merge research into model data
        if not model_data.get("assumptions") or len(model_data.get("assumptions", [])) < 5:
            model_data["assumptions"] = [
                ["Assumption", "Value"],
                ["Revenue Growth Rate", research.get("revenueGrowth", "5%")],
                ["EBITDA Margin", research.get("ebitdaMargin", "20%")],
                ["WACC", research.get("wacc", "10%")],
                ["Terminal Growth Rate", "2.5%"],
                ["Terminal Multiple", research.get("terminalMultiple", "10x")]
            ]

    except Exception as e:
        print(f"Research enhancement failed: {e}")

    return model_data


def get_fallback_template() -> Dict[str, Any]:
    """
    Fallback template if AI generation fails
    """
    return {
        "assumptions": [
            ["Assumption", "Value"],
            ["Revenue Growth Rate (Y1-3)", "8%"],
            ["Revenue Growth Rate (Y4-5)", "5%"],
            ["EBITDA Margin", "22%"],
            ["Tax Rate", "25%"],
            ["CAPEX (% of Revenue)", "3%"],
            ["NWC Change (% of Rev)", "2%"],
            ["Cost of Equity", "12%"],
            ["Cost of Debt", "5%"],
            ["Debt/Equity Ratio", "30%"],
            ["WACC", "10.2%"],
            ["Terminal Growth Rate", "2.5%"]
        ],
        "financials": [
            ["Item", "Year 0", "Year 1", "Year 2", "Year 3", "Year 4", "Year 5"],
            ["Revenue", 1000, "=B2*1.08", "=C2*1.08", "=D2*1.08", "=E2*1.05", "=F2*1.05"],
            ["EBITDA", "=B2*0.22", "=C2*0.22", "=D2*0.22", "=E2*0.22", "=F2*0.22", "=G2*0.22"],
            ["D&A", 50, 55, 60, 65, 68, 71],
            ["EBIT", "=B3-B4", "=C3-C4", "=D3-D4", "=E3-E4", "=F3-F4", "=G3-G4"],
            ["Tax", "=B5*0.25", "=C5*0.25", "=D5*0.25", "=E5*0.25", "=F5*0.25", "=G5*0.25"],
            ["NOPAT", "=B5-B6", "=C5-C6", "=D5-D6", "=E5-E6", "=F5-F6", "=G5-G6"],
            ["+ D&A", "=B4", "=C4", "=D4", "=E4", "=F4", "=G4"],
            ["- CAPEX", "=B2*0.03", "=C2*0.03", "=D2*0.03", "=E2*0.03", "=F2*0.03", "=G2*0.03"],
            ["- NWC Change", "=B2*0.02", "=C2*0.02", "=D2*0.02", "=E2*0.02", "=F2*0.02", "=G2*0.02"],
            ["Free Cash Flow", "=B7+B8-B9-B10", "=C7+C8-C9-C10", "=D7+D8-D9-D10", "=E7+E8-E9-E10", "=F7+F8-F9-F10", "=G7+G8-G9-G10"]
        ],
        "dcfCalculations": [
            ["DCF Calculation", "Year 1", "Year 2", "Year 3", "Year 4", "Year 5"],
            ["Free Cash Flow", "=Financials!C11", "=Financials!D11", "=Financials!E11", "=Financials!F11", "=Financials!G11"],
            ["Discount Factor", "=1/(1+0.102)^1", "=1/(1+0.102)^2", "=1/(1+0.102)^3", "=1/(1+0.102)^4", "=1/(1+0.102)^5"],
            ["PV of FCF", "=B2*B3", "=C2*C3", "=D2*D3", "=E2*E3", "=F2*F3"],
            ["", "", "", "", "", ""],
            ["Sum of PV FCF", "=SUM(B4:F4)", "", "", "", ""],
            ["Terminal Value", "=Financials!G11*(1+0.025)/(0.102-0.025)", "", "", "", ""],
            ["PV of Terminal Value", "=B7*F3", "", "", "", ""],
            ["", "", "", "", "", ""],
            ["Enterprise Value", "=B6+B8", "", "", "", ""],
            ["Less: Net Debt", 200, "", "", "", ""],
            ["Equity Value", "=B10-B11", "", "", "", ""]
        ]
    }
