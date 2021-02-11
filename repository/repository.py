from heuristics.reFile import *
from heuristics.rePytest import *
from heuristics.reUnittest import *
from pydriller import RepositoryMining


class Repository:
    def __init__(self, repo_url):
        # self.pydriller_repo = RepositoryMining(repo_url, only_in_branch="master", only_no_merge=True)
        self.pydriller_repo = RepositoryMining(repo_url, single="b724832872ae4b4cd4b5f61c153eae39f1c3b213")
        self.pytest_first_occurrence = {}
        self.pytest_last_occurrence = {}
        self.unittest_first_occurrence = {}
        self.unittest_last_occurrence = {}
        self.amount_commits_unittest = 0
        self.amount_commits_pytest = 0
        self.amount_commits_both = 0
        self.amount_commits_between = 0

    def traverse_commits(self):
        for commit in self.pydriller_repo.traverse_commits():
            for modification in commit.modifications:
                print(modification.new_path)
                print(modification.old_path)
                if is_a_test_file(modification.new_path) \
                    or is_a_test_file(modification.old_path) \
                    or is_a_config_file(modification.new_path) \
                    or is_a_config_file(modification.old_path):
                    print(modification.diff_parsed)
                    unittest_in_added_diffs = check_unittest(modification.diff_parsed['added'])
                    unittest_in_removed_diffs = check_unittest(modification.diff_parsed['deleted'])
                    pytest_in_added_diffs = check_pytest(modification.diff_parsed['added'])
                    pytest_in_removed_diffs = check_pytest(modification.diff_parsed['deleted'])

                    print(modification.source_code)
                else:
                    pass
                print()
