import re

class UnittestHeuristics:
    pattern =  "(\s*import\s*unittest)"
    pattern += "|(unittest)"
    pattern += "|(\s*from\s*unittest)"

    @classmethod
    def matches_a(cls, text):
        if text == None:
            return False

        return re.search(cls.pattern, text) != None

    @classmethod
    def matches_any(cls, text_list):
        for element in text_list:
            if cls.matches_a(element):
                return True

        return False
