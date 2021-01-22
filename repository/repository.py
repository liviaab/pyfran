class Repository:
    def __init__(self, pd_repo):
        self.pydriller_repo = pd_repo
        self.pytest_first_occurrence = {}
        self.pytest_last_occurrence = {}
        self.unittest_first_occurrence = {}
        self.unittest_last_occurrence = {}
        self.amount_commits_unittest = 0
        self.amount_commits_pytest = 0
        self.amount_commits_both = 0
