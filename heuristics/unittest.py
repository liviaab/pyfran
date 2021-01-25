UNITTEST_REGEX = "(import\s*unittest)" # e.g. import unittest
UNITTEST_REGEX += "|(unittest)" # e.g. class TestStringMethods(unittest.TestCase):
                                # unittest.mock
                                # unittest.main()
UNITTEST_REGEX += "|(TestCase)" # e.g. class TestStringMethods(TestCase):
                                # testcase = unittest.FunctionTestCase(testSomething, ...
                                # asynctest.TestCase
UNITTEST_REGEX += "|(.*from\s*unittest)" # e.g. from unittest.mock import MagicMock
