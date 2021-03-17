class CommitsMetrics:
    def __init__(self):
        self.amount_total_commits = 0
        self.amount_commits_unittest = 0
        self.amount_commits_pytest = 0
        self.amount_commits_both = 0
        self.percentage_migration_commits = 0

    def calculate_migrated_metrics(self, commit_hashes, first_hash_unittest, last_hash_unittest, first_hash_pytest):
        idx_first_unittest_commit = commit_hashes.index(first_hash_unittest)
        idx_last_unittest_commit = commit_hashes.index(last_hash_unittest)
        idx_first_pytest_commit = commit_hashes.index(first_hash_pytest)

        self.amount_total_commits = len(commit_hashes)
        self.amount_commits_both = idx_last_unittest_commit - idx_first_pytest_commit
        self.amount_commits_unittest = idx_last_unittest_commit - idx_first_unittest_commit
        self.amount_commits_pytest = self.amount_total_commits - idx_first_pytest_commit
        self.percentage_migration_commits = round(self.amount_commits_both/self.amount_total_commits * 100, 5)
        return

    def calculate_ongoing_metrics(self, commit_hashes, first_hash_unittest, first_hash_pytest):
        idx_first_unittest_commit = commit_hashes.index(first_hash_unittest)
        idx_first_pytest_commit = commit_hashes.index(first_hash_pytest)

        self.amount_total_commits = len(commit_hashes)
        self.amount_commits_both = self.amount_total_commits - idx_first_pytest_commit
        self.amount_commits_unittest = self.amount_total_commits - idx_first_unittest_commit
        self.amount_commits_pytest = self.amount_total_commits - idx_first_pytest_commit
        self.percentage_migration_commits = round(self.amount_commits_both/self.amount_total_commits * 100, 5)
        return

    def print_metrics(self):
        print('Number of total commits', self.amount_total_commits)
        print('Number of commits using `unittest`', self.amount_commits_unittest)
        print('Number of commits using `pytest`', self.amount_commits_pytest)
        print('Number of commits using `both` ', self.amount_commits_both)
        print('Percentage of migration commits', self.percentage_migration_commits)
