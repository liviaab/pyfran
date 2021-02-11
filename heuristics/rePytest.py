import re

PYTEST_REGEX = "(import\s*pytest)"
PYTEST_REGEX += "|(pytest)"
PYTEST_REGEX += "|(Test)"           # classes que começam com Test
PYTEST_REGEX += "|(test_)"          # funções que começam com Test


def check_pytest(parsed_modifications):
    if code == None or parsed_modifications == []:
        return False

    for line, modification in parsed_modifications:
        matches = re.search(PYTEST_REGEX, code)
        if matches != None:
            return True

    return False
