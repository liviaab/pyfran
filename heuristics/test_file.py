import re

class TestFileHeuristics:
    testpath_pattern = ".*test[s]?.*\.py"

    @classmethod
    def matches_test_file(cls, path):
        return path != None and re.search(cls.testpath_pattern, path) != None
