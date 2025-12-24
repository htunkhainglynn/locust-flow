#!/usr/bin/env python3
"""
Comprehensive test runner for all plugin tests.

This script runs all plugin-related unit tests and provides a summary.
"""
import sys
import unittest

# Discover and run all tests in the plugins directory
loader = unittest.TestLoader()
suite = loader.discover("tests/plugins", pattern="test_*.py")

runner = unittest.TextTestRunner(verbosity=2)
result = runner.run(suite)

# Exit with appropriate code
sys.exit(0 if result.wasSuccessful() else 1)
