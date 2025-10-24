# Testing Directory

This directory contains all test files organized by category for the Web Content Analysis Agent.

## 📁 Directory Structure

### `bulk_analysis/`
Tests for bulk URL analysis functionality:
- `test_comprehensive.py` - Comprehensive test with various URL types and error scenarios
- `test_copy_paste.py` - Test for copy/paste URL functionality 
- `bulk_url_test.py` - Main bulk URL testing script
- `quick_bulk_test.py` - Quick bulk analysis test

### `scripts/`
Shell and PowerShell scripts for testing:
- `bulk_test.ps1` - PowerShell script for bulk testing
- `bulk_test.sh` - Bash script for bulk testing

### `integration/`
Integration and system tests:
- `test_credentials.py` - Test Azure OpenAI credentials and connectivity

### `../tests/` (Unit Tests)
Unit tests for individual components:
- `test_api.py` - API endpoint unit tests
- `test_services.py` - Service layer unit tests
- `conftest.py` - Pytest configuration

## 🚀 Running Tests

### Bulk Analysis Tests
```bash
# Run comprehensive test
python testing/bulk_analysis/test_comprehensive.py

# Test copy/paste functionality  
python testing/bulk_analysis/test_copy_paste.py

# Quick bulk test
python testing/bulk_analysis/quick_bulk_test.py

# Full bulk URL test
python testing/bulk_analysis/bulk_url_test.py
```

### Integration Tests
```bash
# Test credentials
python testing/integration/test_credentials.py
```

### Scripts
```bash
# PowerShell
.\testing\scripts\bulk_test.ps1

# Bash (if available)
bash testing/scripts/bulk_test.sh
```

### Unit Tests
```bash
# Run all unit tests
pytest tests/

# Run specific test file
pytest tests/test_api.py
pytest tests/test_services.py
```

## 📊 Test Coverage

- **Bulk Analysis**: 4 test files covering file upload, copy/paste, and comprehensive scenarios
- **Integration**: Credential and connectivity testing
- **Unit Tests**: API and service layer testing
- **Scripts**: Cross-platform testing scripts

## 🎯 Test Types

### Performance Tests
- `test_comprehensive.py` - Measures timing and success rates
- `bulk_url_test.py` - Tests concurrent processing

### Functionality Tests  
- `test_copy_paste.py` - Copy/paste interface testing
- `quick_bulk_test.py` - Quick functionality verification

### System Tests
- `test_credentials.py` - End-to-end connectivity
- Scripts - Cross-platform compatibility

## 📝 Adding New Tests

When adding new test files:

1. **Bulk Analysis Tests** → `bulk_analysis/`
2. **Integration Tests** → `integration/`  
3. **Cross-platform Scripts** → `scripts/`
4. **Unit Tests** → `../tests/`

## 🔧 Test Data

Test URLs and data files are located in the root directory:
- `test_urls.txt` - Sample URLs for testing
- `bulk_test_results_*.json` - Test result files

---

*Last updated: October 24, 2024*