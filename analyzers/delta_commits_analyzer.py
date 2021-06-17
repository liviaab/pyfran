import os

from pydriller import RepositoryMining
from analyzers.custom_commit import CustomCommit
from analyzers.occurrences import Occurrences

from common.common import VALID_EXTENSIONS
from heuristics.test_file import TestFileHeuristics as fh
from heuristics.pytest import PytestHeuristics as ph
from heuristics.unittest import UnittestHeuristics as uh
from heuristics.apis import UnittestAPIHeuristics as uAPIh, PytestAPIHeuristics as pAPIh

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

            commit_memo = self.__initial_state_commit_memo()
            # print("commit_memo")
            # print(commit_memo)

            for modification in commit.modifications:
                _filename, extension = os.path.splitext(modification.filename)
                if modification.source_code == None or extension not in VALID_EXTENSIONS:
                    continue

                self.__match_patterns(modification)
                self.__update_occurrences(index, commit, modification)

                # check if a reference to pytest/unittest was added or removed
                commit_memo = self.__update_base_commit_memo(commit_memo)

                # check the apis of each framework
                commit_memo = self.__update_memo_unittest_apis(commit_memo, modification)
                commit_memo = self.__update_memo_pytest_apis(commit_memo, modification)

            commit_memo["are_we_interested"] = self.__are_we_interested(commit_memo)
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

    def __update_base_commit_memo(self, commit_memo):
        updated_memo = {
            "unittest_in_code": commit_memo["unittest_in_code"] or self.tmp_memo["unittest_in_code"],
            "unittest_in_removed_diffs": commit_memo["unittest_in_removed_diffs"] or self.tmp_memo["unittest_in_removed_diffs"],
            "pytest_in_code": commit_memo["pytest_in_code"] or self.tmp_memo["pytest_in_code"],
            "pytest_in_removed_diffs": commit_memo["pytest_in_removed_diffs"] or self.tmp_memo["pytest_in_removed_diffs"],
            "has_test_file": commit_memo["has_test_file"] or self.tmp_memo["is_test_file"]
        }

        commit_memo.update(updated_memo)
        return commit_memo

    def __update_memo_unittest_apis(self, commit_memo, modification):
        added_lines = self.__get_lines_from_diff(modification.diff_parsed['added'])
        removed_lines = self.__get_lines_from_diff(modification.diff_parsed['deleted'])

        apis_in_added_lines = uAPIh.check_apis_in_list(added_lines)
        apis_in_removed_lines = uAPIh.check_apis_in_list(removed_lines)

        unittest_memo = {
            "u_count_added_testCaseSubclass": commit_memo["u_count_added_testCaseSubclass"] + apis_in_added_lines["count_testCaseSubclass"],
            "u_count_added_assert": commit_memo["u_count_added_assert"] + apis_in_added_lines["count_assert"],
            "u_count_added_setUp": commit_memo["u_count_added_setUp"] + apis_in_added_lines["count_setUp"],
            "u_count_added_setUpClass": commit_memo["u_count_added_setUpClass"] + apis_in_added_lines["count_setUpClass"],
            "u_count_added_tearDown": commit_memo["u_count_added_tearDown"] + apis_in_added_lines["count_tearDown"],
            "u_count_added_tearDownClass": commit_memo["u_count_added_tearDownClass"] + apis_in_added_lines["count_tearDownClass"],
            "u_count_added_unittestSkipTest": commit_memo["u_count_added_unittestSkipTest"] + apis_in_added_lines["count_unittestSkipTest"],
            "u_count_added_selfSkipTest": commit_memo["u_count_added_selfSkipTest"] + apis_in_added_lines["count_selfSkipTest"],
            "u_count_added_expectedFailure": commit_memo["u_count_added_expectedFailure"] + apis_in_added_lines["count_expectedFailure"],
            "unittest_matches_in_added_lines": {
                "testCaseSubclass": commit_memo["unittest_matches_in_added_lines"]["testCaseSubclass"] + apis_in_added_lines["matches_testCaseSubclass"],
                "assert": commit_memo["unittest_matches_in_added_lines"]["assert"] + apis_in_added_lines["matches_assert"],
                "setUp": commit_memo["unittest_matches_in_added_lines"]["setUp"] + apis_in_added_lines["matches_setUp"],
                "setUpClass": commit_memo["unittest_matches_in_added_lines"]["setUpClass"] + apis_in_added_lines["matches_setUpClass"],
                "tearDown": commit_memo["unittest_matches_in_added_lines"]["tearDown"] + apis_in_added_lines["matches_tearDown"],
                "tearDownClass": commit_memo["unittest_matches_in_added_lines"]["tearDownClass"] + apis_in_added_lines["matches_tearDownClass"],
                "unittestSkipTest": commit_memo["unittest_matches_in_added_lines"]["unittestSkipTest"] + apis_in_added_lines["matches_unittestSkipTest"],
                "selfSkipTest": commit_memo["unittest_matches_in_added_lines"]["selfSkipTest"] + apis_in_added_lines["matches_selfSkipTest"],
                "expectedFailure": commit_memo["unittest_matches_in_added_lines"]["expectedFailure"] + apis_in_added_lines["matches_expectedFailure"]
            },

            "u_count_removed_testCaseSubclass": commit_memo["u_count_removed_testCaseSubclass"] + apis_in_removed_lines["count_testCaseSubclass"],
            "u_count_removed_assert": commit_memo["u_count_removed_assert"] + apis_in_removed_lines["count_assert"],
            "u_count_removed_setUp": commit_memo["u_count_removed_setUp"] + apis_in_removed_lines["count_setUp"],
            "u_count_removed_setUpClass": commit_memo["u_count_removed_setUpClass"] + apis_in_removed_lines["count_setUpClass"],
            "u_count_removed_tearDown": commit_memo["u_count_removed_tearDown"] + apis_in_removed_lines["count_tearDown"],
            "u_count_removed_tearDownClass": commit_memo["u_count_removed_tearDownClass"] + apis_in_removed_lines["count_tearDownClass"],
            "u_count_removed_unittestSkipTest": commit_memo["u_count_removed_unittestSkipTest"] + apis_in_removed_lines["count_unittestSkipTest"],
            "u_count_removed_selfSkipTest": commit_memo["u_count_removed_selfSkipTest"] + apis_in_removed_lines["count_selfSkipTest"],
            "u_count_removed_expectedFailure": commit_memo["u_count_removed_expectedFailure"] + apis_in_removed_lines["count_expectedFailure"],
            "unittest_matches_in_removed_lines": {
                "testCaseSubclass": commit_memo["unittest_matches_in_removed_lines"]["testCaseSubclass"] + apis_in_removed_lines["matches_testCaseSubclass"],
                "assert": commit_memo["unittest_matches_in_removed_lines"]["assert"] + apis_in_removed_lines["matches_assert"],
                "setUp": commit_memo["unittest_matches_in_removed_lines"]["setUp"] + apis_in_removed_lines["matches_setUp"],
                "setUpClass": commit_memo["unittest_matches_in_removed_lines"]["setUpClass"] + apis_in_removed_lines["matches_setUpClass"],
                "tearDown": commit_memo["unittest_matches_in_removed_lines"]["tearDown"] + apis_in_removed_lines["matches_tearDown"],
                "tearDownClass": commit_memo["unittest_matches_in_removed_lines"]["tearDownClass"] + apis_in_removed_lines["matches_tearDownClass"],
                "unittestSkipTest": commit_memo["unittest_matches_in_removed_lines"]["unittestSkipTest"] + apis_in_removed_lines["matches_unittestSkipTest"],
                "selfSkipTest": commit_memo["unittest_matches_in_removed_lines"]["selfSkipTest"] + apis_in_removed_lines["matches_selfSkipTest"],
                "expectedFailure": commit_memo["unittest_matches_in_removed_lines"]["expectedFailure"] + apis_in_removed_lines["matches_expectedFailure"]
            }
        }

        commit_memo.update(unittest_memo)
        return commit_memo

    def __update_memo_pytest_apis(self, commit_memo, modification):
        added_lines = self.__get_lines_from_diff(modification.diff_parsed['added'])
        removed_lines = self.__get_lines_from_diff(modification.diff_parsed['deleted'])

        apis_in_added_lines = pAPIh.check_apis_in_list(added_lines)
        apis_in_removed_lines = pAPIh.check_apis_in_list(removed_lines)

        pytest_memo = {
            "p_count_added_native_assert": commit_memo["p_count_added_native_assert"] + apis_in_added_lines["count_native_assert"],
            "p_count_added_pytestRaise": commit_memo["p_count_added_pytestRaise"] + apis_in_added_lines["count_pytestRaise"],
            "p_count_added_simpleSkip": commit_memo["p_count_added_simpleSkip"] + apis_in_added_lines["count_simpleSkip"],
            "p_count_added_markSkip": commit_memo["p_count_added_markSkip"] + apis_in_added_lines["count_markSkip"],
            "p_count_added_expectedFailure": commit_memo["p_count_added_expectedFailure"] + apis_in_added_lines["count_expectedFailure"],
            "p_count_added_fixture": commit_memo["p_count_added_fixture"] + apis_in_added_lines["count_fixture"],
            "p_count_added_usefixture": commit_memo["p_count_added_usefixture"] + apis_in_added_lines["count_usefixture"],
            "p_count_added_generalMark": commit_memo["p_count_added_generalMark"] + apis_in_added_lines["count_generalMark"],
            "p_count_added_generalPytest": commit_memo["p_count_added_generalPytest"] + apis_in_added_lines["count_generalPytest"],
            "pytest_matches_in_added_lines": {
                "native_assert": commit_memo["pytest_matches_in_added_lines"]["native_assert"] + apis_in_added_lines["matches_native_assert"],
                "pytestRaise": commit_memo["pytest_matches_in_added_lines"]["pytestRaise"] + apis_in_added_lines["matches_pytestRaise"],
                "simpleSkip": commit_memo["pytest_matches_in_added_lines"]["simpleSkip"] + apis_in_added_lines["matches_simpleSkip"],
                "markSkip": commit_memo["pytest_matches_in_added_lines"]["markSkip"] + apis_in_added_lines["matches_markSkip"],
                "expectedFailure": commit_memo["pytest_matches_in_added_lines"]["expectedFailure"] + apis_in_added_lines["matches_expectedFailure"],
                "fixture": commit_memo["pytest_matches_in_added_lines"]["fixture"] + apis_in_added_lines["matches_fixture"],
                "usefixture": commit_memo["pytest_matches_in_added_lines"]["usefixture"] + apis_in_added_lines["matches_usefixture"],
                "generalMark": commit_memo["pytest_matches_in_added_lines"]["generalMark"] + apis_in_added_lines["matches_generalMark"],
                "generalPytest": commit_memo["pytest_matches_in_added_lines"]["generalPytest"] + apis_in_added_lines["matches_generalPytest"]
            },

            "p_count_removed_native_assert": commit_memo["p_count_removed_native_assert"] + apis_in_removed_lines["count_native_assert"],
            "p_count_removed_pytestRaise": commit_memo["p_count_removed_pytestRaise"] + apis_in_removed_lines["count_pytestRaise"],
            "p_count_removed_simpleSkip": commit_memo["p_count_removed_simpleSkip"] + apis_in_removed_lines["count_simpleSkip"],
            "p_count_removed_markSkip": commit_memo["p_count_removed_markSkip"] + apis_in_removed_lines["count_markSkip"],
            "p_count_removed_expectedFailure": commit_memo["p_count_removed_expectedFailure"] + apis_in_removed_lines["count_expectedFailure"],
            "p_count_removed_fixture": commit_memo["p_count_removed_fixture"] + apis_in_removed_lines["count_fixture"],
            "p_count_removed_usefixture": commit_memo["p_count_removed_usefixture"] + apis_in_removed_lines["count_usefixture"],
            "p_count_removed_generalMark": commit_memo["p_count_removed_generalMark"] + apis_in_removed_lines["count_generalMark"],
            "p_count_removed_generalPytest": commit_memo["p_count_removed_generalPytest"] + apis_in_removed_lines["count_generalPytest"],
            "pytest_matches_in_removed_lines": {
                "native_assert": commit_memo["pytest_matches_in_removed_lines"]["native_assert"] + apis_in_removed_lines["matches_native_assert"],
                "pytestRaise": commit_memo["pytest_matches_in_removed_lines"]["pytestRaise"] + apis_in_removed_lines["matches_pytestRaise"],
                "simpleSkip": commit_memo["pytest_matches_in_removed_lines"]["simpleSkip"] + apis_in_removed_lines["matches_simpleSkip"],
                "markSkip": commit_memo["pytest_matches_in_removed_lines"]["markSkip"] + apis_in_removed_lines["matches_markSkip"],
                "expectedFailure": commit_memo["pytest_matches_in_removed_lines"]["expectedFailure"] + apis_in_removed_lines["matches_expectedFailure"],
                "fixture": commit_memo["pytest_matches_in_removed_lines"]["fixture"] + apis_in_removed_lines["matches_fixture"],
                "usefixture": commit_memo["pytest_matches_in_removed_lines"]["usefixture"] + apis_in_removed_lines["matches_usefixture"],
                "generalMark": commit_memo["pytest_matches_in_removed_lines"]["generalMark"] + apis_in_removed_lines["matches_generalMark"],
                "generalPytest": commit_memo["pytest_matches_in_removed_lines"]["generalPytest"] + apis_in_removed_lines["matches_generalPytest"]
            }
        }

        commit_memo.update(pytest_memo)
        return commit_memo

    def __are_we_interested(self, commit_memo):
        return bool(commit_memo["unittest_in_code"] or commit_memo["unittest_in_removed_diffs"] \
                or commit_memo["pytest_in_code"] or commit_memo["pytest_in_removed_diffs"] \
                or commit_memo["u_count_added_testCaseSubclass"] \
                or commit_memo["u_count_added_assert"] or commit_memo["u_count_added_setUp"] \
                or commit_memo["u_count_added_setUpClass"] or commit_memo["u_count_added_tearDown"] \
                or commit_memo["u_count_added_tearDownClass"] or commit_memo["u_count_added_unittestSkipTest"] \
                or commit_memo["u_count_added_selfSkipTest"] or commit_memo["u_count_added_expectedFailure"] \
                or commit_memo["u_count_removed_testCaseSubclass"] or commit_memo["u_count_removed_assert"] \
                or commit_memo["u_count_removed_setUp"] or commit_memo["u_count_removed_setUpClass"] \
                or commit_memo["u_count_removed_tearDown"] or commit_memo["u_count_removed_tearDownClass"] \
                or commit_memo["u_count_removed_unittestSkipTest"] or commit_memo["u_count_removed_selfSkipTest"] \
                or commit_memo["u_count_removed_expectedFailure"] or commit_memo["p_count_added_native_assert"] \
                or commit_memo["p_count_added_pytestRaise"] or commit_memo["p_count_added_simpleSkip"] \
                or commit_memo["p_count_added_markSkip"] or commit_memo["p_count_added_expectedFailure"] \
                or commit_memo["p_count_added_fixture"] or commit_memo["p_count_added_usefixture"] \
                or commit_memo["p_count_added_generalMark"] or commit_memo["p_count_added_generalPytest"] \
                or commit_memo["p_count_removed_native_assert"] or commit_memo["p_count_removed_pytestRaise"] \
                or commit_memo["p_count_removed_simpleSkip"] or commit_memo["p_count_removed_markSkip"] \
                or commit_memo["p_count_removed_expectedFailure"] or commit_memo["p_count_removed_fixture"] \
                or commit_memo["p_count_removed_usefixture"] or commit_memo["p_count_removed_generalMark"] \
                or commit_memo["p_count_removed_generalPytest"])

    def __initial_state_commit_memo(self):
        return {
                "unittest_in_code": False,
                "unittest_in_removed_diffs": False,
                "pytest_in_code": False,
                "pytest_in_removed_diffs": False,
                "has_test_file": False,
                "are_we_interested": False,

                "u_count_added_testCaseSubclass": 0,
                "u_count_added_assert": 0,
                "u_count_added_setUp": 0,
                "u_count_added_setUpClass": 0,
                "u_count_added_tearDown": 0,
                "u_count_added_tearDownClass": 0,
                "u_count_added_unittestSkipTest": 0,
                "u_count_added_selfSkipTest": 0,
                "u_count_added_expectedFailure": 0,
                "unittest_matches_in_added_lines": {
                    "testCaseSubclass": [],
                    "assert": [],
                    "setUp": [],
                    "setUpClass": [],
                    "tearDown": [],
                    "tearDownClass": [],
                    "unittestSkipTest": [],
                    "selfSkipTest": [],
                    "expectedFailure": []
                },

                "u_count_removed_testCaseSubclass": 0,
                "u_count_removed_assert": 0,
                "u_count_removed_setUp": 0,
                "u_count_removed_setUpClass": 0,
                "u_count_removed_tearDown": 0,
                "u_count_removed_tearDownClass": 0,
                "u_count_removed_unittestSkipTest": 0,
                "u_count_removed_selfSkipTest": 0,
                "u_count_removed_expectedFailure": 0,
                "unittest_matches_in_removed_lines": {
                    "testCaseSubclass": [],
                    "assert": [],
                    "setUp": [],
                    "setUpClass": [],
                    "tearDown": [],
                    "tearDownClass": [],
                    "unittestSkipTest": [],
                    "selfSkipTest": [],
                    "expectedFailure": [],
                },

                "p_count_added_native_assert": 0,
                "p_count_added_pytestRaise": 0,
                "p_count_added_simpleSkip": 0,
                "p_count_added_markSkip": 0,
                "p_count_added_expectedFailure": 0,
                "p_count_added_fixture": 0,
                "p_count_added_usefixture": 0,
                "p_count_added_generalMark": 0,
                "p_count_added_generalPytest": 0,
                "pytest_matches_in_added_lines": {
                    "native_assert": [],
                    "pytestRaise": [],
                    "simpleSkip": [],
                    "markSkip": [],
                    "expectedFailure": [],
                    "fixture": [],
                    "usefixture": [],
                    "generalMark": [],
                    "generalPytest": [],
                },

                "p_count_removed_native_assert": 0,
                "p_count_removed_pytestRaise": 0,
                "p_count_removed_simpleSkip": 0,
                "p_count_removed_markSkip": 0,
                "p_count_removed_expectedFailure": 0,
                "p_count_removed_fixture": 0,
                "p_count_removed_usefixture": 0,
                "p_count_removed_generalMark": 0,
                "p_count_removed_generalPytest": 0,
                "pytest_matches_in_removed_lines": {
                    "native_assert": [],
                    "pytestRaise": [],
                    "simpleSkip": [],
                    "markSkip": [],
                    "expectedFailure": [],
                    "fixture": [],
                    "usefixture": [],
                    "generalMark": [],
                    "generalPytest": [],
                }
            }