# Test Data

This directory contains sample files for testing backend services.

## Files

- **sample_company.txt**: Sample company data for testing PDF extraction and model generation
- **sample_model.json**: Complete DCF model structure for testing error checking
- **model_with_errors.json**: Model with intentional errors (#DIV/0!, #REF!) for testing error detection

## Usage

Run tests with:
```bash
cd backend
uv run python test_services.py
```

## Adding More Test Data

Create new files following these patterns:
- Company data: `.txt` files with financial information
- Model data: `.json` files matching the Excel model structure
- Expected outputs: `.json` files with expected test results
