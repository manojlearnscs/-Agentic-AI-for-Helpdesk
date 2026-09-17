import unittest
import sys
import os

# Ensure project root is in python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from tests.test_agent import TestITHelpdeskAgent

if __name__ == "__main__":
    print("\n=======================================================")
    print("Running AI IT Helpdesk Agent Test Suite")
    print("=======================================================\n")
    unittest.main(verbosity=2)
