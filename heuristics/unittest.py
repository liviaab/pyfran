from pyparsing import Keyword, pythonStyleComment, quotedString
from common.common import docString

class UnittestHeuristics:
    keyword = "unittest"

    @classmethod
    def matches_a(cls, text, ignoreComments=True):
        if text == None:
            return False

        expr = Keyword(cls.keyword).ignore(quotedString | docString)
        if ignoreComments:
            expr = Keyword(cls.keyword).ignore(pythonStyleComment | quotedString | docString)

        return list(expr.scanString(text)) != []

    @classmethod
    def matches_any(cls, text_list, ignoreComments=True):
        for element in text_list:
            if cls.matches_a(element, ignoreComments):
                return True

        return False
