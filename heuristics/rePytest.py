import re

class PytestHeuristics:
    pattern = "(pytest)"
    subclass_pattern = "\s*class\s*.*\(.+\).*"
    test_function_pattern = "(def\s*test_)"

    def matches_a(self, text):
        if text == None:
            return False

        return re.search(PytestHeuristics.pattern, text) != None

    def matches_any(self, text_list):
        for element in text_list:
            if matches_a(element):
                return True

        return False

    def matches_testfuncion(self, text):
        function_match = re.search(TEST_REGEX, source_code)
        subclass_match = re.search(SUBCLASS_REGEX, source_code)
        return function_match != None and subclass_match == None

    def matches_testfuncion_in_list(self, text_list):
        for element in text_list:
            if matches_testfuncion(element):
                return True

        return False
