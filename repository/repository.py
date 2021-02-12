from heuristics.reFile import *
from heuristics.rePytest import *
from heuristics.reUnittest import *
from pydriller import RepositoryMining


class Repository:
    def __init__(self, repo_url):
        print('repo')
        print(repo_url)
        self.pydriller_repo = RepositoryMining(repo_url, only_in_branch="master", only_no_merge=True)
        # self.pydriller_repo = RepositoryMining(repo_url, single="65fc888172fbff89a8354e8926a69b4515766389")
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
                if is_a_test_file(modification.new_path) \
                    or is_a_test_file(modification.old_path) \
                    or is_a_config_file(modification.new_path) \
                    or is_a_config_file(modification.old_path):
                    # print(modification.new_path)
                    unittest_in_added_diffs = check_unittest_code(modification.source_code)
                    unittest_in_removed_diffs = check_unittest(modification.diff_parsed['deleted'])

                    # testar para fazer isso \/ se não tiver unittest_in_added_diffs ? 
                    pytest_in_added_diffs = check_pytest_code(modification.source_code)
                    pytest_in_removed_diffs = check_pytest(modification.diff_parsed['deleted'])

                    if self.pytest_first_occurrence == {} and pytest_in_added_diffs:
                        self.pytest_first_occurrence = {
                            "file": modification.new_path,
                            "author": commit.author.name,
                            "date": commit.author_date,
                            "commit_hash": commit.hash,
                            "commit_message": commit.msg,
                        }

                    if pytest_in_removed_diffs and not pytest_in_added_diffs:
                        pytest_last_occurrence = {
                            "file": modification.new_path,
                            "author": commit.author.name,
                            "date": commit.author_date,
                            "commit_hash": commit.hash,
                            "commit_message": commit.msg,
                        }

                    if self.unittest_first_occurrence == {} and unittest_in_added_diffs:
                        self.unittest_first_occurrence = {
                            "file": modification.new_path,
                            "author": commit.author.name,
                            "date": commit.author_date,
                            "commit_hash": commit.hash,
                            "commit_message": commit.msg,
                        }

                    if unittest_in_removed_diffs and not unittest_in_added_diffs:
                        self.unittest_last_occurrence = {
                            "file": modification.new_path,
                            "author": commit.author.name,
                            "date": commit.author_date,
                            "commit_hash": commit.hash,
                            "commit_message": commit.msg,
                        }
                    # print(modification.source_code)
                else:
                    pass
        print('pytest_first_occurrence')
        print(self.pytest_first_occurrence)
        print('pytest_last_occurrence')
        print(self.pytest_last_occurrence)
        print('unittest_first_occurrence')
        print(self.unittest_first_occurrence)
        print('unittest_last_occurrence')
        print(self.unittest_last_occurrence)
        print()
