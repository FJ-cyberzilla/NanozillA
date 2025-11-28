#!/usr/bin/env python3
"""
Test runner script for NANozILLA Reactor
"""

import subprocess
import sys
import os


def run_tests():
    """Run all tests and return exit code"""
    print("🚀 Running NANozILLA Reactor Test Suite...")
    print("=" * 50)

    # Run pytest with coverage
    result = subprocess.run([
        sys.executable, "-m", "pytest",
        "tests/",
        "-v",
        "--tb=short",
        "--disable-warnings"
    ], cwd=os.path.dirname(os.path.abspath(__file__)))

    print("=" * 50)

    if result.returncode == 0:
        print("✅ All tests passed!")
    elif result.returncode == 5:
        print("⚠️  No tests collected - check test discovery")
    else:
        print("❌ Some tests failed")

    return result.returncode


if __name__ == "__main__":
    sys.exit(run_tests())
