import re
from pyparsing import Keyword, QuotedString, pythonStyleComment, quotedString

docString = QuotedString(quoteChar='"""', multiline=True, unquoteResults=False)

class UnittestHeuristics:
    keyword = "unittest"

    @classmethod
    def matches_a(cls, text):
        if text == None:
            return False

        expr = Keyword(cls.keyword).ignore(pythonStyleComment | quotedString | docString)
        return list(expr.scanString(text)) != []

    @classmethod
    def matches_any(cls, text_list):
        for element in text_list:
            if cls.matches_a(element):
                return True

        return False
