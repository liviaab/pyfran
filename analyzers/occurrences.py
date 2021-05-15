from analyzers.custom_commit import CustomCommit

class Occurrences:
    def __init__(self):
        self.first = CustomCommit()
        self.last = CustomCommit()

    def set_first_occurrence(self, index, commit):
        self.first.setCommit(index, commit)
        return

    def set_last_occurrence(self, index, commit):
        self.last.setCommit(index, commit)
        return

    def has_first_occurrence(self):
        return self.first != {}

    def has_last_occurrence(self):
        return self.last != {}
