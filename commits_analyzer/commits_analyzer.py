from heuristics.file import FileHeuristics
from heuristics.pytest import PytestHeuristics
from heuristics.unittest import UnittestHeuristics
from pydriller import RepositoryMining
from commits_analyzer.commits_metrics import CommitsMetrics
from commits_analyzer.occurrences import Occurrences

class CommitsAnalyzer:
    def __init__(self, repo_url):
        self.miner = RepositoryMining(repo_url, only_in_branch="master", only_no_merge=True)
        self.project_name = repo_url.split('/')[-1]
        self.metrics = CommitsMetrics()
        self.unittest_occurrences = Occurrences()
        self.pytest_occurrences = Occurrences()
        self.memo = {
            "unittest_in_added_diffs": False,
            "unittest_in_removed_diffs": False,
            "pytest_in_added_diffs": False,
            "pytest_in_removed_diffs": False,
            "testfunction_in_code": False,
            "testfunction_in_removed_diffs": False,
            "is_test_file": False
        }

    def process_commits(self):
        print("\nAnalyzing ", self.project_name, "...")
        for commit in self.miner.traverse_commits():
            self.metrics.commit_hashes.append(commit.hash)
            for modification in commit.modifications:
                if modification.source_code == None:
                    continue

                self.__match_patterns(modification)
                self.__update_occurrences(commit, modification)

        print("Analyzed", len(self.metrics.commit_hashes), " commits.")
        return

    def process_metrics(self):
        first_hash_unittest = self.unittest_occurrences.first['commit_hash']
        last_hash_unittest = self.unittest_occurrences.last['commit_hash']
        first_hash_pytest = self.pytest_occurrences.first['commit_hash']

        self.metrics.calculate(first_hash_unittest, last_hash_unittest, first_hash_pytest)
        return

    def __get_lines_from_diff(self, parsed_modifications):
        return [ removed_line for line, removed_line in parsed_modifications ]

    def __match_patterns(self, modification):
        removed_lines = self.__get_lines_from_diff(modification.diff_parsed['deleted'])

        self.memo = {
            "unittest_in_added_diffs": UnittestHeuristics.matches_a(modification.source_code),
            "unittest_in_removed_diffs": UnittestHeuristics.matches_any(removed_lines),
            "pytest_in_added_diffs": PytestHeuristics.matches_a(modification.source_code),
            "pytest_in_removed_diffs": PytestHeuristics.matches_any(removed_lines),
            "testfunction_in_code": PytestHeuristics.matches_testfuncion(modification.source_code),
            "testfunction_in_removed_diffs": PytestHeuristics.matches_testfuncion_in_list(removed_lines),
            "is_test_file": FileHeuristics.matches_test_file(modification.new_path)
        }
        return

    def __update_occurrences(self, commit, modification):
        if (not self.unittest_occurrences.has_first_occurrence()) \
            and self.memo["unittest_in_added_diffs"]:
            self.unittest_occurrences.set_first_occurrence(commit, modification)

        if self.memo["unittest_in_removed_diffs"] and (not self.memo["unittest_in_added_diffs"]):
            self.unittest_occurrences.set_last_occurrence(commit, modification)

        if (not self.pytest_occurrences.has_first_occurrence()) \
            and (self.memo["pytest_in_added_diffs"] \
                or (self.memo["is_test_file"] \
                    and self.memo["testfunction_in_code"] \
                    and not self.memo["unittest_in_added_diffs"]
                )
            ):
            self.pytest_occurrences.set_first_occurrence(commit, modification)

        if self.memo["pytest_in_removed_diffs"] and not self.memo["pytest_in_added_diffs"] \
            or (not self.memo["unittest_in_removed_diffs"] \
                and not self.memo["pytest_in_removed_diffs"] \
                and self.memo["testfunction_in_removed_diffs"]):
            self.pytest_occurrences.set_last_occurrence(commit, modification)

        return
