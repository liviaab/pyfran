PYTEST_REGEX = "import\s*pytest"
PYTEST_REGEX += "|@pytest" # @pytest.fixture, @pytest.mark.asyncio
PYTEST_REGEX += "|pytest"

def check_pytest(code):
    return code != None and re.search(PYTEST_REGEX, code) != None
