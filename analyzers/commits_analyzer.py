from heuristics.file import FileHeuristics
from heuristics.pytest import PytestHeuristics
from heuristics.unittest import UnittestHeuristics
from pydriller import RepositoryMining
from analyzers.commits_metrics import CommitsMetrics
from analyzers.occurrences import Occurrences
from analyzers.repository_analyzer import RepositoryAnalyzer

class CommitsAnalyzer:
    def __init__(self, repo_url):
        self.repo_url = repo_url
        self.miner = RepositoryMining(repo_url, only_in_branch="master", only_no_merge=True)
        self.project_name = repo_url.split('/')[-1]
        self.commit_hashes = []
        self.metrics = CommitsMetrics()
        self.unittest_occurrences = Occurrences()
        self.pytest_occurrences = Occurrences()
        self.memo = {
            "unittest_in_code": False,
            "unittest_in_removed_diffs": False,
            "pytest_in_code": False,
            "pytest_in_removed_diffs": False,
            "testfunction_in_code": False,
            "testfunction_in_removed_diffs": False,
            "is_test_file": False
        }

    def process_commits(self):
        print("\nAnalyzing", self.project_name, "...")
        for commit in self.miner.traverse_commits():
            self.commit_hashes.append(commit.hash)
            for modification in commit.modifications:
                if modification.source_code == None:
                    continue

                self.__match_patterns(modification)
                self.__update_occurrences(commit, modification)

        print("Analyzed", len(self.commit_hashes), " commits.")
        return

    def classify_and_process_metrics(self):
        """
            return: (class, metrics)

            classes: unittest | pytest | ongoing | migrated

            metrics for ongoing and migrated repositories:
                (
                    quantity of unittest commits,
                    quantity of pytest commits,
                    quantity of commits containing both frameworks,
                )

            metrics for pytest or unittest only repositories:
                quantity of total commits
        """
        if not self.unittest_occurrences.has_first_occurrence() \
            and self.pytest_occurrences.has_first_occurrence():

            return 'pytest', len(self.commit_hashes)

        if not self.pytest_occurrences.has_first_occurrence() \
            and self.unittest_occurrences.has_first_occurrence():
            print("This is a unittest repository since the beginning")
            return 'unittest', len(self.commit_hashes)

        if (self.unittest_occurrences.has_first_occurrence() \
            and self.pytest_occurrences.has_first_occurrence()):
            currentDefaultBranch = RepositoryAnalyzer(self.repo_url)
            currentDefaultBranch.search_frameworks()

            if(currentDefaultBranch.usesPytest and not currentDefaultBranch.usesUnittest):
                print("This repository was migrated")
                first_hash_unittest = self.unittest_occurrences.first['commit_hash']
                last_hash_unittest = self.unittest_occurrences.last['commit_hash']
                first_hash_pytest = self.pytest_occurrences.first['commit_hash']
                self.metrics.calculate_migrated_metrics(self.commit_hashes, first_hash_unittest, last_hash_unittest, first_hash_pytest)
                self.metrics.print_metrics()

                metrics = (len(self.commit_hashes), \
                    self.metrics.amount_commits_unittest, \
                    self.metrics.amount_commits_pytest, \
                    self.metrics.amount_commits_both
                )
                return 'migrated', metrics

            if(currentDefaultBranch.usesPytest and currentDefaultBranch.usesUnittest):
                print("This repository is using both frameworks")
                first_hash_unittest = self.unittest_occurrences.first['commit_hash']
                first_hash_pytest = self.pytest_occurrences.first['commit_hash']
                self.metrics.calculate_ongoing_metrics(self.commit_hashes, first_hash_unittest, first_hash_pytest)
                self.metrics.print_metrics()

                metrics = (len(self.commit_hashes), \
                    self.metrics.amount_commits_unittest, \
                    self.metrics.amount_commits_pytest, \
                    self.metrics.amount_commits_both
                )
                return 'ongoing', metrics

        print("Unexpected control flow")
        return

    def __get_lines_from_diff(self, parsed_modifications):
        return [ removed_line for line, removed_line in parsed_modifications ]

    def __match_patterns(self, modification):
        removed_lines = self.__get_lines_from_diff(modification.diff_parsed['deleted'])

        self.memo = {
            "unittest_in_code": UnittestHeuristics.matches_a(modification.source_code),
            "unittest_in_removed_diffs": UnittestHeuristics.matches_any(removed_lines),
            "pytest_in_code": PytestHeuristics.matches_a(modification.source_code),
            "pytest_in_removed_diffs": PytestHeuristics.matches_any(removed_lines),
            "testfunction_in_code": PytestHeuristics.matches_testfuncion(modification.source_code),
            "testfunction_in_removed_diffs": PytestHeuristics.matches_testfuncion_in_list(removed_lines),
            "is_test_file": FileHeuristics.matches_test_file(modification.new_path)
        }
        return

    def __update_occurrences(self, commit, modification):
        if (not self.unittest_occurrences.has_first_occurrence()) \
            and self.memo["unittest_in_code"]:
            self.unittest_occurrences.set_first_occurrence(commit, modification)

        if self.unittest_occurrences.has_first_occurrence() \
            and (self.memo["unittest_in_removed_diffs"] and (not self.memo["unittest_in_code"])):
            self.unittest_occurrences.set_last_occurrence(commit, modification)

        if (not self.pytest_occurrences.has_first_occurrence()) \
            and (self.memo["pytest_in_code"]):
            self.pytest_occurrences.set_first_occurrence(commit, modification)


        if self.pytest_occurrences.has_first_occurrence() \
            and self.memo["pytest_in_removed_diffs"] and not self.memo["pytest_in_code"] \
            or (not self.memo["unittest_in_removed_diffs"] \
                and not self.memo["pytest_in_removed_diffs"] \
                and self.memo["testfunction_in_removed_diffs"]):
            self.pytest_occurrences.set_last_occurrence(commit, modification)

        return
