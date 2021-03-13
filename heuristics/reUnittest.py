import re

class UnittestHeuristics:
    pattern =  "(\s*import\s*unittest)"
    pattern += "|(unittest)"
    pattern += "|(\s*from\s*unittest)"

    def matches_a(self, text):
        if text == None:
            return False

        return re.search(UnittestHeuristics.pattern, text) != None

    def matches_any(self, text_list):
        for element in text_list:
            if matches_a(element):
                return True

        return False
