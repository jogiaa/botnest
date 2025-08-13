#!/usr/bin/env python3
"""
Test runner script for tree_hugger2.0.py unit tests.
This script runs all tests and provides a summary of results.
"""

import sys
import unittest
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def run_tests():
    """Run all unit tests and return results."""
    # Discover and run tests
    loader = unittest.TestLoader()
    start_dir = os.path.dirname(os.path.abspath(__file__))
    suite = loader.discover(start_dir, pattern='test_*.py')
    
    # Run tests with verbose output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result

def main():
    """Main function to run tests."""
    print("=" * 60)
    print("Running Unit Tests for tree_hugger2.0.py")
    print("=" * 60)
    
    try:
        result = run_tests()
        
        print("\n" + "=" * 60)
        print("TEST SUMMARY")
        print("=" * 60)
        print(f"Tests run: {result.testsRun}")
        print(f"Failures: {len(result.failures)}")
        print(f"Errors: {len(result.errors)}")
        print(f"Skipped: {len(result.skipped)}")
        
        if result.failures:
            print("\nFAILURES:")
            for test, traceback in result.failures:
                print(f"  {test}: {traceback}")
        
        if result.errors:
            print("\nERRORS:")
            for test, traceback in result.errors:
                print(f"  {test}: {traceback}")
        
        if result.wasSuccessful():
            print("\n✅ All tests passed successfully!")
            return 0
        else:
            print("\n❌ Some tests failed!")
            return 1
            
    except Exception as e:
        print(f"\n❌ Error running tests: {e}")
        return 1

if __name__ == '__main__':
    sys.exit(main()) 