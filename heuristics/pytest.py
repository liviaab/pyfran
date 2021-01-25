PYTEST_REGEX = "import\s*pytest"
PYTEST_REGEX += "|@pytest" # @pytest.fixture, @pytest.mark.asyncio
PYTEST_REGEX += "|pytest"
