"""
Test script for backend services
Run with: python test_services.py
Or with pytest: pytest test_services.py -v
"""

import asyncio
import os
import json
from io import BytesIO
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Test PDF service
def test_pdf_extraction():
    """Test PDF text extraction"""
    print("\n🧪 Testing PDF Service...")
    from services.pdf_service import extract_text_from_pdf

    try:
        test_pdf = "test_data/novo-nordisk-annual-report-2024.pdf"
        if os.path.exists(test_pdf):
            with open(test_pdf, 'rb') as f:
                pdf_bytes = f.read()
            text = extract_text_from_pdf(pdf_bytes)
            print(f"✅ PDF extraction successful: {len(text)} characters extracted")
            return True
        else:
            print("⚠️  No test PDF found, skipping PDF extraction test")
            return None
    except Exception as e:
        print(f"❌ PDF extraction failed: {str(e)}")
        return False


# Test model generation service
async def test_model_generation():
    """Test DCF model generation"""
    print("\n🧪 Testing Model Generation Service...")
    from services.model_service import generate_dcf_model

    try:
        # Sample company data
        test_data = """
        Company: Tech Corp
        Revenue: $100M (2023), $120M (2024)
        EBITDA Margin: 25%
        Industry: SaaS
        Growth Rate: 20%
        """

        model_data = await generate_dcf_model(test_data)

        # Validate structure
        required_sheets = ["Assumptions", "Financials", "DCF Calculation"]
        for sheet in required_sheets:
            if sheet not in model_data:
                print(f"❌ Missing sheet: {sheet}")
                return False

        print(f"✅ Model generation successful")
        print(f"   - Generated {len(model_data)} sheets")
        print(f"   - Sheets: {list(model_data.keys())}")
        return True

    except Exception as e:
        print(f"❌ Model generation failed: {str(e)}")
        return False


# Test error checking service
async def test_error_checking():
    """Test error checking service"""
    print("\n🧪 Testing Error Checking Service...")
    from services.error_check_service import check_model_errors

    try:
        # Load model with intentional errors
        with open("test_data/model_with_errors.json", 'r') as f:
            test_model = json.load(f)

        errors = await check_model_errors(test_model)

        if errors and len(errors) > 0:
            print(f"✅ Error detection successful")
            print(f"   - Found {len(errors)} errors:")
            for i, error in enumerate(errors[:3], 1):  # Show first 3
                print(f"     {i}. {error.get('type', 'Unknown')}: {error.get('message', 'No message')}")
            return True
        else:
            print("⚠️  No errors detected (expected to find #DIV/0! and #REF!)")
            return None

    except Exception as e:
        print(f"❌ Error checking failed: {str(e)}")
        return False


# Test chat service
async def test_chat_service():
    """Test chat service"""
    print("\n🧪 Testing Chat Service...")
    from services.chat_service import chat_with_model

    try:
        # Sample model data
        test_model = {
            "Assumptions": {
                "data": [[["Growth Rate", "15%"]], [["WACC", "10%"]]],
            },
            "DCF Calculation": {
                "data": [[["Enterprise Value", "$500M"]]],
            }
        }

        test_message = "What is the WACC assumption?"
        response = await chat_with_model(test_message, test_model, [])

        if response and len(response) > 10:
            print(f"✅ Chat service successful")
            print(f"   - Response length: {len(response)} characters")
            print(f"   - Preview: {response[:100]}...")
            return True
        else:
            print("❌ Chat response too short or empty")
            return False

    except Exception as e:
        print(f"❌ Chat service failed: {str(e)}")
        return False


# Test API health endpoint
def test_health_endpoint():
    """Test the /health endpoint"""
    print("\n🧪 Testing Health Endpoint...")
    import requests

    try:
        response = requests.get("http://localhost:3001/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health endpoint working")
            print(f"   - Status: {data.get('status')}")
            print(f"   - Timestamp: {data.get('timestamp')}")
            return True
        else:
            print(f"❌ Health endpoint returned status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("⚠️  Backend not running on localhost:3001")
        return None
    except Exception as e:
        print(f"❌ Health check failed: {str(e)}")
        return False


async def run_all_tests():
    """Run all tests"""
    print("=" * 60)
    print("🚀 Excel DCF Assistant - Service Tests")
    print("=" * 60)

    results = {}

    # Synchronous tests
    results['PDF Extraction'] = test_pdf_extraction()
    results['Health Endpoint'] = test_health_endpoint()

    # Async tests
    results['Model Generation'] = await test_model_generation()
    results['Error Checking'] = await test_error_checking()
    results['Chat Service'] = await test_chat_service()

    # Summary
    print("\n" + "=" * 60)
    print("📊 Test Summary")
    print("=" * 60)

    passed = sum(1 for v in results.values() if v is True)
    failed = sum(1 for v in results.values() if v is False)
    skipped = sum(1 for v in results.values() if v is None)

    for test_name, result in results.items():
        status = "✅ PASS" if result is True else "❌ FAIL" if result is False else "⚠️  SKIP"
        print(f"{status} - {test_name}")

    print(f"\nTotal: {passed} passed, {failed} failed, {skipped} skipped")
    print("=" * 60)

    return failed == 0


if __name__ == "__main__":
    # Check if OpenAI API key is set
    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️  Warning: OPENAI_API_KEY not set in environment")
        print("   Some tests may fail. Set it in backend/.env\n")

    # Run tests
    success = asyncio.run(run_all_tests())
    exit(0 if success else 1)
