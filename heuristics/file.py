import re

class FileHeuristics:
    testpath_pattern = "(test)"

    @classmethod
    def matches_test_file(cls, path):
        return path != None and re.search(cls.testpath_pattern, path) != None
