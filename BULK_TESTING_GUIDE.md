# Bulk URL Testing Guide
=======================

This directory contains several scripts to test the bulk analysis capabilities of your Web Content Analysis Agent.

## 🚀 Available Test Scripts

### 1. **Python Async Test** (`bulk_url_test.py`)
- **Advanced concurrent testing** with detailed reporting
- Tests 15 diverse URLs from different categories and languages
- Generates comprehensive JSON reports with statistics
- Best for: Performance testing and detailed analysis

**Usage:**
```bash
python bulk_url_test.py
```

### 2. **Quick Python Test** (`quick_bulk_test.py`)
- **Simple sequential testing** with 5 URLs
- Easy to understand and modify
- Good for quick validation
- Best for: Quick testing and debugging

**Usage:**
```bash
python quick_bulk_test.py
```

### 3. **PowerShell Test** (`bulk_test.ps1`)
- **Windows-native testing** with colored output
- Interactive results directory opening
- Category accuracy measurement
- Best for: Windows users and integration testing

**Usage:**
```powershell
.\bulk_test.ps1
```

### 4. **Bash/Curl Test** (`bulk_test.sh`)
- **Command-line testing** using curl
- Works in Git Bash, WSL, or Linux
- Raw HTTP testing approach
- Best for: System integration and CI/CD pipelines

**Usage:**
```bash
chmod +x bulk_test.sh
./bulk_test.sh
```

## 📊 Test Coverage

The bulk tests cover these content types:

| Category | Example URLs | Language |
|----------|-------------|----------|
| **Satirical News** | Le Gorafi | French |
| **Sports** | Le Parisien Sports | French |
| **Technology** | BBC Tech, TechCrunch | English |
| **Health** | Mayo Clinic, Doctissimo | English/French |
| **Travel** | Lonely Planet, Routard | English/French |
| **Business** | Reuters, Bloomberg | English |
| **Science** | National Geographic | English |
| **Finance** | Bloomberg Markets | English |
| **Entertainment** | IMDB | English |
| **Lifestyle** | AllRecipes, Marmiton | English/French |
| **Documentation** | Python Docs | English |
| **Forums** | Stack Overflow | English |

## 🎯 What Gets Tested

Each test validates:
- ✅ **Category Detection Accuracy**
- ✅ **Sentiment Analysis**
- ✅ **Content Summarization** 
- ✅ **Entity Extraction**
- ✅ **Processing Performance**
- ✅ **Error Handling**
- ✅ **Multi-language Support**

## 📈 Expected Results

### **Performance Metrics:**
- Processing time: 2-8 seconds per URL
- Success rate: >90%
- Category accuracy: >80%
- Concurrent processing: 3-5 URLs simultaneously

### **Category Examples:**
- Le Gorafi → `"satire"` or `"humor"`
- Sports sites → `"sports"`
- Tech news → `"technology"`
- Health sites → `"health"`
- Travel guides → `"travel"`

## 🔧 Prerequisites

1. **Server Running:** Ensure your API is running at `http://127.0.0.1:8000`
2. **Dependencies:** Install required packages:
   ```bash
   pip install aiohttp requests
   ```
3. **Network Access:** Internet connection for fetching web content

## 📁 Results

All tests generate results in the `test_results/` directory:
- Individual response files
- Summary statistics
- Error logs
- Performance metrics

## 🚨 Troubleshooting

### Common Issues:

**Server Not Running:**
```bash
python -m uvicorn src.main:app --reload --host 127.0.0.1 --port 8000
```

**Connection Refused:**
- Check if port 8000 is available
- Verify server is listening on 127.0.0.1

**Timeout Errors:**
- Some websites may be slow to load
- Increase timeout values in scripts
- Check internet connection

**Category Mismatches:**
- Expected - your dynamic system can generate any appropriate category
- AI might use more specific categories (e.g., "investigative_journalism" instead of "news")

## 🎉 Success Indicators

A successful bulk test should show:
- ✅ 80%+ success rate
- ✅ Diverse category detection
- ✅ Appropriate sentiment analysis
- ✅ Reasonable processing times
- ✅ No server crashes or memory issues

## 🔄 Customization

You can easily modify the test URLs in any script to test:
- Your specific content types
- Different languages
- Specific domains or competitors
- Custom categories you want to validate

Happy testing! 🚀