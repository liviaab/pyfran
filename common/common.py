# Valid extensions to search for unittest and pytest patterns
# We need this to filter which files to analyze, otherwise
# it would take a lot more time to process and classify

VALID_EXTENSIONS = ['.py', '.yaml', '.yml', '.txt', '.rst', '.md', '.ini', '.toml', '.cfg', '.sh']

# Custom pattern to ignore docstrings
from pyparsing import QuotedString
docString = QuotedString(quoteChar='"""', multiline=True, unquoteResults=False)
