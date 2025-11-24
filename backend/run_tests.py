#!/usr/bin/env python3
"""Test runner with coverage report"""
import sys
import subprocess

def run_tests():
    """Run all tests with coverage"""
    print("🧪 Running tests with coverage...\n")
    
    result = subprocess.run([
        "pytest",
        "--cov=app",
        "--cov-report=term-missing",
        "--cov-report=html:htmlcov",
        "--cov-fail-under=70",
        "-v"
    ])
    
    if result.returncode == 0:
        print("\n✅ All tests passed!")
        print("📊 Coverage report: htmlcov/index.html")
        return 0
    else:
        print("\n❌ Tests failed!")
        return 1

if __name__ == "__main__":
    sys.exit(run_tests())
