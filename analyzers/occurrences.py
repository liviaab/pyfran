class Occurrences:
    def __init__(self):
        self.first = {}
        self.last = {}

    def set_first_occurrence(self, commit, modification):
        self.first = {
            "file": modification.new_path,
            "author": commit.author.name,
            "date": commit.author_date,
            "commit_hash": commit.hash,
            "commit_message": commit.msg,
            "project_name": commit.project_name,
            "source_code": modification.source_code
        }
        return

    def set_last_occurrence(self, commit, modification):
        self.last = {
            "file": modification.new_path,
            "author": commit.author.name,
            "date": commit.author_date,
            "commit_hash": commit.hash,
            "commit_message": commit.msg,
            "project_name": commit.project_name,
            "source_code": modification.source_code
        }
        return

    def has_first_occurrence(self):
        return self.first != {}

    def has_last_occurrence(self):
        return self.last != {}
