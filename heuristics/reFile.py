import re

class FileHeuristics:
    testpath_pattern = "(test)"

    def matches_test_file(path):
        return path != None and re.search(testpath_pattern, path) != None
