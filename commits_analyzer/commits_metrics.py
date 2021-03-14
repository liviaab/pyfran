class CommitsMetrics:
    def __init__(self):
        self.commit_hashes = []
        self.amount_commits_unittest = 0
        self.amount_commits_pytest = 0
        self.amount_commits_both = 0
        self.percentage_migration_commits = 0


    """
        Calculates the inteval between commits

        param: first_hash_unittest - commit hash for the first occurrence of unittest
        param: last_hash_unittest - commit hash for the last occurrence of unittest

        param: first_hash_pytest - commit hash for the first occurrence of pytest
        param: last_hash_pytest - commit hash for the last occurrence of pytest

        This method can only be used for migrated repositories

    """
    def calculate(self, first_hash_unittest, last_hash_unittest, first_hash_pytest):
        idx_first_unittest_commit = self.commit_hashes.index(first_hash_unittest)
        idx_last_unittest_commit = self.commit_hashes.index(last_hash_unittest)
        idx_first_pytest_commit = self.commit_hashes.index(first_hash_pytest)

        amount_total_commits = len(self.commit_hashes)
        print(idx_first_unittest_commit, idx_last_unittest_commit, idx_first_pytest_commit)
        self.amount_commits_both = idx_last_unittest_commit - idx_first_pytest_commit
        self.amount_commits_unittest = idx_last_unittest_commit - idx_first_unittest_commit
        self.amount_commits_pytest = amount_total_commits - 1 - idx_first_pytest_commit
        self.percentage_migration_commits = round(self.amount_commits_both/amount_total_commits * 100, 5)

        return