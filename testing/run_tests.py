import sys
import os
import unittest
from pathlib import Path

# Add the parent directory to the path so we can import Backend modules
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / 'Backend'))

def run_tests():
    # Run all unit tests

    # Test loader
    loader = unittest.TestLoader()

    # Discover tests in the testing directory
    test_dir = Path(__file__).parent
    suite = loader.discover(str(test_dir), pattern='test_*.py')

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Return exit code based on results
    return 0 if result.wasSuccessful() else 1

if __name__ == '__main__':
    sys.exit(run_tests())