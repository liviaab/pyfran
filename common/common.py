# Valid extensions to search for unittest and pytest patterns
# We need this to filter which files to analyze, otherwise
# it would take a lot more time to process and classify

VALID_EXTENSIONS = ['.py', '.yaml', '.yml', '.txt', '.md', '.ini', '.toml']

# Custom pattern to ignore docstrings
from pyparsing import QuotedString
docString = QuotedString(quoteChar='"""', multiline=True, unquoteResults=False)

# Valid tags that we can attribute to a migration commit
TAGS = [
    "assert_migration",
    "fixture_migration",
    "test_function_migration"
]