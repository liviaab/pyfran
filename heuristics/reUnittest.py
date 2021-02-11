import re

UNITTEST_REGEX = "(\s*import\s*unittest)" # ex. import unittest
UNITTEST_REGEX += "|(unittest)" # ex. class TestStringMethods(unittest.TestCase):
                                # unittest.mock
                                # unittest.main()
UNITTEST_REGEX += "|(TestCase)" # ex. class TestStringMethods(TestCase):
                                # testcase = unittest.FunctionTestCase(testSomething, ...
                                # asynctest.TestCase
                                # class DefaultWidgetSizeTestCase
UNITTEST_REGEX += "|(\s*from\s*unittest)" # ex. from unittest.mock import MagicMock
UNITTEST_REGEX += "|(test)"     # métodos que iniciam com test
UNITTEST_REGEX += "|(Test\.*)"  # classes que iniciam com Test


def check_unittest(parsed_modifications):
    if code == None or parsed_modifications == []:
        return False

    for line, modification in parsed_modifications:
        matches = re.search(UNITTEST_REGEX, code)
        if matches != None:
            return True

    return False
