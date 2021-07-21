from pyparsing import Regex, pythonStyleComment, quotedString
from common.common import docString

class PytestHeuristics:
    regex = "(\s+pytest\Z|\s+pytest\s+)"

    @classmethod
    def matches_a(cls, text, ignoreComments=True):
        if text == None:
            return False

        expr = Regex(cls.regex).ignore(quotedString | docString)
        if ignoreComments:
            expr = Regex(cls.regex).ignore(pythonStyleComment | quotedString | docString)

        return list(expr.scanString(text)) != []

    @classmethod
    def matches_any(cls, text_list, ignoreComments=True):
        for element in text_list:
            if cls.matches_a(element, ignoreComments):
                return True

        return False
