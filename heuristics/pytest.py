import re

class PytestHeuristics:
    pattern = "(\s+pytest\s+)"
    subclass_pattern = "\s*class\s*.*\(.+\).*"
    test_function_pattern = "(def\s*test_)"

    @classmethod
    def matches_a(cls, text):
        if text == None:
            return False

        return re.search(cls.pattern, text) != None

    @classmethod
    def matches_any(cls, text_list):
        for element in text_list:
            if cls.matches_a(element):
                return True

        return False

    @classmethod
    def matches_testfuncion(cls, text):
        if text == None:
            return False

        function_match = re.search(cls.test_function_pattern, text)
        subclass_match = re.search(cls.subclass_pattern, text)
        return function_match != None and subclass_match == None

    @classmethod
    def matches_testfuncion_in_list(cls, text_list):
        for element in text_list:
            if cls.matches_testfuncion(element):
                return True

        return False
