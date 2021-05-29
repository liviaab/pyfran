import re

class TestMethodsHeuristics:
    pattern = "def\s+test_"

    @classmethod
    def count_test_methods(cls, content):
        return len(re.findall(cls.pattern, content))
