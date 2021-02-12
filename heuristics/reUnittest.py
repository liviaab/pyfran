import re

UNITTEST_REGEX = "(\s*import\s*unittest)" # ex. import unittest
UNITTEST_REGEX += "|(unittest)" # ex. class TestStringMethods(unittest.TestCase):
                                # unittest.mock
                                # unittest.main()
# UNITTEST_REGEX += "|(unittest.TestCase)" # ex. class TestStringMethods(TestCase):
                                # testcase = unittest.FunctionTestCase(testSomething, ...
                                # asynctest.TestCase
                                # class DefaultWidgetSizeTestCase
                                # incluso no anterior
UNITTEST_REGEX += "|(\s*from\s*unittest)" # ex. from unittest.mock import MagicMock
# UNITTEST_REGEX += "|(test)"     # métodos que iniciam com test << também dá match com pytest
# UNITTEST_REGEX += "|(Test\.*)"  # classes que iniciam com Test << também pode dar match com pytest


def check_unittest(parsed_modifications):
    if parsed_modifications == None or parsed_modifications == []:
        return False

    for line, modification in parsed_modifications:
        matches = re.search(UNITTEST_REGEX, modification)
        if matches != None:
            return True

    return False

def check_unittest_code(source_code):
    if source_code == None:
        return False

    return re.search(UNITTEST_REGEX, source_code) != None
