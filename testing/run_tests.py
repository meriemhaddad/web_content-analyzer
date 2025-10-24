#!/usr/bin/env python3
"""
Test Runner for Web Content Analysis Agent

This script provides an easy way to run all tests in the testing directory.
"""

import os
import sys
import subprocess
import time
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def run_command(command, description):
    """Run a command and return success status."""
    print(f"\n[TEST] {description}")
    print("-" * 50)
    
    try:
        result = subprocess.run(command, shell=True, cwd=project_root, 
                              capture_output=True, text=True, timeout=300)
        
        if result.returncode == 0:
            print(f"[SUCCESS] {description} - PASSED")
            if result.stdout:
                print(result.stdout)
            return True
        else:
            print(f"[ERROR] {description} - FAILED")
            if result.stderr:
                print(f"Error: {result.stderr}")
            if result.stdout:
                print(f"Output: {result.stdout}")
            return False
            
    except subprocess.TimeoutExpired:
        print(f"⏰ {description} - TIMEOUT (5 minutes)")
        return False
    except Exception as e:
        print(f"[EXCEPTION] {description} - EXCEPTION: {str(e)}")
        return False

def main():
    """Run all tests."""
    print("[RUNNING] Web Content Analysis Agent - Test Runner")
    print("=" * 60)
    
    # Check if server is running
    print("\n[INFO] Checking if FastAPI server is running...")
    server_check = subprocess.run(
        "curl -s http://127.0.0.1:8000/docs > nul 2>&1", 
        shell=True, capture_output=True
    )
    
    if server_check.returncode != 0:
        print("[WARNING]  FastAPI server not detected. Please start the server:")
        print("   python -m uvicorn src.main:app --reload --host 127.0.0.1 --port 8000")
        print("\nRunning tests that don't require the server...\n")
        server_running = False
    else:
        print("[SUCCESS] FastAPI server is running")
        server_running = True
    
    results = []
    
    # Unit Tests (don't require server)
    print("\n" + "="*60)
    print("[RESULTS] UNIT TESTS")
    print("="*60)
    
    if os.path.exists(project_root / "tests"):
        results.append(run_command("python -m pytest tests/ -v", "Unit Tests"))
    else:
        print("[WARNING]  Unit tests directory not found")
    
    if not server_running:
        print("\n[WARNING]  Skipping integration tests - server not running")
        return
    
    # Integration Tests (require server)
    print("\n" + "="*60)
    print("[SYMBOL] INTEGRATION TESTS")
    print("="*60)
    
    # Credentials test
    results.append(run_command(
        "python testing/integration/test_credentials.py", 
        "Credentials & Connectivity Test"
    ))
    
    # Bulk Analysis Tests
    print("\n" + "="*60)
    print("[STATS] BULK ANALYSIS TESTS")
    print("="*60)
    
    results.append(run_command(
        "python testing/bulk_analysis/quick_bulk_test.py", 
        "Quick Bulk Test"
    ))
    
    results.append(run_command(
        "python testing/bulk_analysis/test_copy_paste.py", 
        "Copy/Paste Functionality Test"
    ))
    
    results.append(run_command(
        "python testing/bulk_analysis/test_comprehensive.py", 
        "Comprehensive URL Analysis Test"
    ))
    
    # Summary
    print("\n" + "="*60)
    print("[SUMMARY] TEST SUMMARY")
    print("="*60)
    
    passed = sum(results)
    total = len(results)
    success_rate = (passed / total * 100) if total > 0 else 0
    
    print(f"[SUCCESS] Passed: {passed}")
    print(f"[ERROR] Failed: {total - passed}")
    print(f"[STATS] Success Rate: {success_rate:.1f}%")
    
    if passed == total:
        print("\n[COMPLETE] All tests passed! Your application is working correctly.")
        return 0
    else:
        print(f"\n[WARNING]  {total - passed} test(s) failed. Please check the output above.")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)