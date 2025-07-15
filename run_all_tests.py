#!/usr/bin/env python3
"""
Master test runner for DeepScribe
Runs all integration tests in the correct order
"""

import subprocess
import sys
import time
from pathlib import Path

def run_test_file(test_file: str, description: str) -> bool:
    """Run a specific test file and return success status"""
    print(f"\n{'='*60}")
    print(f"🧪 Running {description}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run([
            sys.executable, test_file
        ], capture_output=False, text=True, timeout=300)
        
        success = result.returncode == 0
        
        if success:
            print(f"✅ {description} - ALL TESTS PASSED")
        else:
            print(f"❌ {description} - TESTS FAILED")
        
        return success
        
    except subprocess.TimeoutExpired:
        print(f"⏰ {description} - TESTS TIMED OUT")
        return False
    except Exception as e:
        print(f"💥 {description} - ERROR: {str(e)}")
        return False

def check_server_health() -> bool:
    """Check if the development server is running"""
    import requests
    try:
        response = requests.get("http://127.0.0.1:5328/api/health", timeout=5)
        return response.status_code == 200
    except:
        return False

def main():
    """Run all DeepScribe tests"""
    print("🚀 DeepScribe Complete Test Suite")
    print("=" * 60)
    print("This will run comprehensive tests for the entire DeepScribe system:")
    print("  1. Q&A Integration Tests")
    print("  2. Complete End-to-End Flow Tests")
    print("=" * 60)
    
    # Check if server is running
    if not check_server_health():
        print("❌ Development server is not running!")
        print("Please start the server with: pnpm dev")
        print("Then run this test suite again.")
        return False
    
    print("✅ Development server is running")
    
    # Define test suite
    test_suite = [
        ("test_qa_integration.py", "Q&A Integration Tests"),
        ("test_complete_flow.py", "Complete End-to-End Flow Tests"),
    ]
    
    # Run all tests
    passed = 0
    failed = 0
    
    for test_file, description in test_suite:
        if Path(test_file).exists():
            success = run_test_file(test_file, description)
            if success:
                passed += 1
            else:
                failed += 1
        else:
            print(f"❌ Test file not found: {test_file}")
            failed += 1
    
    # Print final summary
    print(f"\n{'='*60}")
    print(f"🏁 FINAL TEST SUMMARY")
    print(f"{'='*60}")
    print(f"✅ Test suites passed: {passed}")
    print(f"❌ Test suites failed: {failed}")
    print(f"📊 Total test suites: {passed + failed}")
    
    if failed == 0:
        print(f"\n🎉 ALL TESTS PASSED! 🎉")
        print("DeepScribe is fully functional and ready for use!")
        print("\nKey features verified:")
        print("  ✅ Patient data extraction from medical transcripts")
        print("  ✅ RAG-powered clinical trial search")
        print("  ✅ LLM-based eligibility filtering and ranking")
        print("  ✅ Interactive Q&A for clinical trials")
        print("  ✅ Complete end-to-end workflow")
        return True
    else:
        print(f"\n⚠️  {failed} test suite(s) failed")
        print("Please review the test output above and fix any issues.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)