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
            # print(commit.author_date, commit.hash)
            for modification in commit.modifications:
                unittest_in_added_diffs = check_unittest_code(modification.source_code)
                unittest_in_removed_diffs = check_unittest(modification.diff_parsed['deleted'])

                pytest_in_added_diffs = check_pytest_code(modification.source_code)
                pytest_in_removed_diffs = check_pytest(modification.diff_parsed['deleted'])

                if self.unittest_first_occurrence == {} and unittest_in_added_diffs:
                    self.unittest_first_occurrence = {
                        "file": modification.new_path,
                        "author": commit.author.name,
                        "date": str(commit.author_date),
                        "commit_hash": commit.hash,
                        "commit_message": commit.msg,
                        "project_name": commit.project_name,
                        "source_code": modification.source_code
                    }

                if unittest_in_removed_diffs and not unittest_in_added_diffs:
                    self.unittest_last_occurrence = {
                        "file": modification.new_path,
                        "author": commit.author.name,
                        "date": str(commit.author_date),
                        "commit_hash": commit.hash,
                        "commit_message": commit.msg,
                        "project_name": commit.project_name,
                        "source_code": modification.source_code
                    }

                if (self.pytest_first_occurrence == {} and pytest_in_added_diffs) \
                    or (self.pytest_first_occurrence == {} \
                        and (not unittest_in_added_diffs) \
                        and (not pytest_in_added_diffs) \
                        and check_src_for_test_function(modification.source_code)):
                    self.pytest_first_occurrence = {
                        "file": modification.new_path,
                        "author": commit.author.name,
                        "date": str(commit.author_date),
                        "commit_hash": commit.hash,
                        "commit_message": commit.msg,
                        "project_name": commit.project_name,
                        "source_code": modification.source_code
                    }

                if pytest_in_removed_diffs and not pytest_in_added_diffs \
                    or (not unittest_in_removed_diffs \
                    and not pytest_in_removed_diffs \
                    and check_diff_for_test_function(modification.diff_parsed['deleted'])):
                    self.pytest_last_occurrence = {
                        "file": modification.new_path,
                        "author": commit.author.name,
                        "date": str(commit.author_date),
                        "commit_hash": commit.hash,
                        "commit_message": commit.msg,
                        "project_name": commit.project_name,
                        "source_code": modification.source_code
                    }
