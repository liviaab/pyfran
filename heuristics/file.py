FILEPATH_REGEX = ".*[test].*"
# FILEPATH_PYTEST_REGEX = "|.*test_.*[.py]"

def is_a_test_file(path):
    return path != None and re.search(FILEPATH_REGEX, path) != None
