import re

# PYTEST_REGEX = "(import\s*pytest)"
PYTEST_REGEX = "(pytest)"
# PYTEST_REGEX += "|(Test)"             # classes que começam com Test << também pode dar match com unittest
# PYTEST_REGEX += "|(test_)"            # funções que começam com Test << também pode dar match com unittest
                                        # mas precisamos de algo para identificar o arquivo de teste caso ele
                                        # não importe pytest explicitamente


def check_pytest(parsed_modifications):
    if parsed_modifications == None or parsed_modifications == []:
        return False

    for line, modification in parsed_modifications:
        matches = re.search(PYTEST_REGEX, modification)
        if matches != None:
            return True

    return False


def check_pytest_code(source_code):
    if source_code == None:
        return False

    return re.search(PYTEST_REGEX, source_code) != None
