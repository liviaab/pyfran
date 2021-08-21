import re
from pyparsing import Regex, pythonStyleComment, dblQuotedString, sglQuotedString, quotedString
from common.common import docString

class PytestHeuristics:
    regex = "pytest(?!-mock)"

    @classmethod
    def matches_a(cls, text, ignoreComments=True):
        if text == None or text.strip() == '':
            return False

        expr = Regex(r'.*').ignore(quotedString | dblQuotedString | sglQuotedString | docString)
        if ignoreComments:
            expr = Regex(r'.*').ignore(pythonStyleComment | quotedString | dblQuotedString | sglQuotedString | docString)

        filtered_result = list(expr.scanString(text))
        filtered_result = [ re.sub("[\"|\'](.*)[\"|\']", "", text[0]) for (text, _, _ ) in filtered_result]
        matches = []
        for result in filtered_result:
            match = re.findall(cls.regex, result)
            if match != []:
                matches.append(match[0])

        return matches != []

    @classmethod
    def matches_any(cls, text_list, ignoreComments=True):
        for element in text_list:
            if cls.matches_a(element, ignoreComments):
                return True

        return False
