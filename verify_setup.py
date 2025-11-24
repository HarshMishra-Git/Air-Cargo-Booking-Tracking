#!/usr/bin/env python3
"""Verify system setup and readiness"""
import os
import sys

def check_file(path, name):
    if os.path.exists(path):
        print(f"[OK] {name}")
        return True
    else:
        print(f"[MISSING] {name}")
        return False

def main():
    print("Verifying Air Cargo System Setup\n")
    
    checks = [
        ("backend/app/main.py", "Backend main"),
        ("backend/app/core/metrics.py", "Prometheus metrics"),
        ("backend/tests/test_cache.py", "Cache tests"),
        ("backend/tests/test_locks.py", "Lock tests"),
        ("backend/tests/test_integration.py", "Integration tests"),
        ("frontend/src/components/MetricsDisplay.tsx", "Metrics display"),
        ("docker-compose.yml", "Docker compose"),
        ("ARCHITECTURE.md", "HLD documentation"),
        ("DETAILED_DESIGN.md", "LLD documentation"),
        ("README.md", "README"),
    ]
    
    results = [check_file(path, name) for path, name in checks]
    
    print(f"\nResults: {sum(results)}/{len(results)} checks passed")
    
    if all(results):
        print("\nSystem is ready for submission!")
        return 0
    else:
        print("\nSome files are missing")
        return 1

if __name__ == "__main__":
    sys.exit(main())
