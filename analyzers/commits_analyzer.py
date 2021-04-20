from pydriller import RepositoryMining
from pyparsing import pythonStyleComment

from heuristics.file import FileHeuristics as fh
from heuristics.pytest import PytestHeuristics as ph
from heuristics.unittest import UnittestHeuristics as uh

from analyzers.commits_metrics import CommitsMetrics
from analyzers.occurrences import Occurrences
from analyzers.repository_analyzer import RepositoryAnalyzer

class CommitsAnalyzer:
    def __init__(self, repo_url):
        self.repo_url = repo_url
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
            "is_test_file": False
        }

    def process_commits(self):
        print("\nAnalyzing {}...".format(self.project_name))
        try:
            self.__process_commits("master")
        except:
            self.__process_commits("main")

        print("Analyzed", len(self.commit_hashes), " commits.")
        return

    def __process_commits(self, branch):
        miner = RepositoryMining(self.repo_url, only_no_merge=True)
        for commit in miner.traverse_commits():
            self.commit_hashes.append(commit.hash)

            for modification in commit.modifications:
                if modification.source_code == None:
                    continue
                self.__match_patterns(modification)
                self.__update_occurrences(commit, modification)


    def classify_and_process_metrics(self):
        """
            return: (class, metrics)

            classes: unittest | pytest | ongoing | migrated | undefined

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
            print("This is a pytest repository since the beginning")
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
        return 'undefined', 0

    def __get_lines_from_diff(self, parsed_modifications):
        return [ removed_line for line, removed_line in parsed_modifications ]

    def __match_patterns(self, modification):
        removed_lines = self.__get_lines_from_diff(modification.diff_parsed['deleted'])

        self.memo = {
            "unittest_in_code": uh.matches_a(modification.source_code),
            "unittest_in_removed_diffs": uh.matches_any(removed_lines, ignoreComments=False),
            "pytest_in_code": ph.matches_a(modification.source_code),
            "pytest_in_removed_diffs": ph.matches_any(removed_lines, ignoreComments=False),
            "is_test_file": fh.matches_test_file(modification.new_path)
        }

        return

    def __update_occurrences(self, commit, modification):
        if self.__can_update_unittest_first_occurrence():
            self.unittest_occurrences.set_first_occurrence(commit, modification)

        if self.__can_update_unittest_last_occurrence():
            self.unittest_occurrences.set_last_occurrence(commit, modification)

        if self.__can_update_pytest_first_occurrence():
            self.pytest_occurrences.set_first_occurrence(commit, modification)

        if self.__can_update_pytest_last_occurrence():
            self.pytest_occurrences.set_last_occurrence(commit, modification)

        return

    def __can_update_unittest_first_occurrence(self):
        return (not self.unittest_occurrences.has_first_occurrence()) \
            and self.memo["unittest_in_code"]

    def __can_update_pytest_first_occurrence(self):
        return (not self.pytest_occurrences.has_first_occurrence()) \
            and self.memo["pytest_in_code"]

    def __can_update_unittest_last_occurrence(self):
        return self.unittest_occurrences.has_first_occurrence() \
                and (self.memo["unittest_in_removed_diffs"])

    def __can_update_pytest_last_occurrence(self):
        return self.pytest_occurrences.has_first_occurrence() \
            and self.memo["pytest_in_removed_diffs"]
