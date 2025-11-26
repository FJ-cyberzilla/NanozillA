import pytest
import sys
import os

# Add project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@pytest.fixture(autouse=True)
def setup_test_environment():
    """Setup test environment for all tests"""
    # Add any global test setup here
    yield
    # Add any global test teardown here
