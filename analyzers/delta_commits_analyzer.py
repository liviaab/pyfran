import os

from pydriller import RepositoryMining
from analyzers.custom_commit import CustomCommit
from analyzers.occurrences import Occurrences

from common.common import VALID_EXTENSIONS
from heuristics.test_file import TestFileHeuristics as fh
from heuristics.pytest import PytestHeuristics as ph
from heuristics.unittest import UnittestHeuristics as uh

class DeltaCommits:
    def __init__(self, repo_url):
        self.repo_url = repo_url
        self.project_name = repo_url.split('/')[-1]
        self.unittest_occurrences = Occurrences()
        self.pytest_occurrences = Occurrences()
        self.tmp_memo = {
            "unittest_in_code": False,
            "unittest_in_removed_diffs": False,
            "pytest_in_code": False,
            "pytest_in_removed_diffs": False,
            "is_test_file": False
        }
        self.allcommits = []

    def process_delta_commits(self):
        print("Analyzing {}...".format(self.project_name))

        index = 0
        for commit in RepositoryMining(self.repo_url, only_no_merge=True).traverse_commits():
            print("\t\tcommit {}".format(commit.hash))

            commit_memo = {
                "unittest_in_code": False,
                "unittest_in_removed_diffs": False,
                "pytest_in_code": False,
                "pytest_in_removed_diffs": False,
                "has_test_file": False
            }

            for modification in commit.modifications:
                _filename, extension = os.path.splitext(modification.filename)
                if modification.source_code == None or extension not in VALID_EXTENSIONS:
                    continue

                self.__match_patterns(modification)
                self.__update_occurrences(index, commit, modification)

                commit_memo = {
                    "unittest_in_code": commit_memo["unittest_in_code"] or self.tmp_memo["unittest_in_code"],
                    "unittest_in_removed_diffs": commit_memo["unittest_in_removed_diffs"] or self.tmp_memo["unittest_in_removed_diffs"],
                    "pytest_in_code": commit_memo["pytest_in_code"] or self.tmp_memo["pytest_in_code"],
                    "pytest_in_removed_diffs": commit_memo["pytest_in_removed_diffs"] or self.tmp_memo["pytest_in_removed_diffs"],
                    "has_test_file": commit_memo["has_test_file"] or self.tmp_memo["is_test_file"]
                }

            custom = CustomCommit(index, commit, commit_memo)
            self.allcommits.append(custom.commit)
            index += 1
        
        print("Analyzed {} commits.".format(len(self.allcommits)))
        
        return (self.allcommits, self.unittest_occurrences, self.pytest_occurrences)

    def __get_lines_from_diff(self, parsed_modifications):
        return [ removed_line for line, removed_line in parsed_modifications ]

    def __match_patterns(self, modification):
        removed_lines = self.__get_lines_from_diff(modification.diff_parsed['deleted'])

        self.tmp_memo = {
            "unittest_in_code": uh.matches_a(modification.source_code),
            "unittest_in_removed_diffs": uh.matches_any(removed_lines, ignoreComments=False),
            "pytest_in_code": ph.matches_a(modification.source_code),
            "pytest_in_removed_diffs": ph.matches_any(removed_lines, ignoreComments=False),
            "is_test_file": fh.matches_test_file(modification.new_path)
        }

        return

    def __update_occurrences(self, index, commit, modification):
        if self.__can_update_unittest_first_occurrence():
            self.unittest_occurrences.set_first_occurrence(index, commit)

        if self.__can_update_unittest_last_occurrence():
            self.unittest_occurrences.set_last_occurrence(index, commit)

        if self.__can_update_pytest_first_occurrence():
            self.pytest_occurrences.set_first_occurrence(index, commit)

        if self.__can_update_pytest_last_occurrence():
            self.pytest_occurrences.set_last_occurrence(index, commit)

        return

    def __can_update_unittest_first_occurrence(self):
        return (not self.unittest_occurrences.has_first_occurrence()) \
            and self.tmp_memo["unittest_in_code"]

    def __can_update_pytest_first_occurrence(self):
        return (not self.pytest_occurrences.has_first_occurrence()) \
            and self.tmp_memo["pytest_in_code"]

    def __can_update_unittest_last_occurrence(self):
        return self.unittest_occurrences.has_first_occurrence() \
                and (self.tmp_memo["unittest_in_removed_diffs"])

    def __can_update_pytest_last_occurrence(self):
        return self.pytest_occurrences.has_first_occurrence() \
            and self.tmp_memo["pytest_in_removed_diffs"]
