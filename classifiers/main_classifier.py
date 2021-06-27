from datetime import datetime, timezone

from analyzers.repository_analyzer import RepositoryAnalyzer
from analyzers.custom_commit import CustomCommit


class MainClassifier:
    def __init__(self, repo_url, allCommits, unittest_occurrences, pytest_occurrences):
        self.repo_url = repo_url
        self.project_name = repo_url.split('/')[-1]
        self.allCommits = allCommits
        self.amount_total_commits = len(allCommits)
        self.currentDefaultBranch = RepositoryAnalyzer(self.repo_url)
        self.unittest_occurrences = unittest_occurrences
        self.pytest_occurrences = pytest_occurrences
        pass

    def classify_and_process_metrics(self):
        """
            classes: unittest | pytest | ongoing | migrated | unknown
        """

        self.currentDefaultBranch.search_frameworks()

        author_infos = []

        base = self.__initial_state()

        if self.__is_pytest_repository():
            author_infos = CustomCommit.characterize_authors(self.allCommits)
            data = self.__build_pytest_repository_data()
            base.update(data)
            return (base, author_infos)

        if self.__is_unittest_repository():
            author_infos = CustomCommit.characterize_authors(self.allCommits)
            data = self.__build_unittest_repository_data()
            base.update(data)
            return (base, author_infos)

        if self.__is_not_pytest_neither_unittest():
            author_infos = CustomCommit.characterize_authors(self.allCommits)
            data = self.__build_not_pytest_neither_unittest_data()
            base.update(data)
            return (base, author_infos)

        idx_first_unittest_commit = CustomCommit.indexOf(self.allCommits, self.unittest_occurrences.first.commit["commit_hash"])

        idx_first_pytest_commit = CustomCommit.indexOf(self.allCommits, self.pytest_occurrences.first.commit["commit_hash"])

        if self.__is_migrated_repository(idx_first_unittest_commit, idx_first_pytest_commit):
            idx_last_unittest_commit = CustomCommit.indexOf(self.allCommits, self.unittest_occurrences.last.commit["commit_hash"])
            author_infos = CustomCommit.characterize_authors(self.allCommits, idx_first_pytest_commit, idx_last_unittest_commit)
            data = self.__build_migrated_repository_data(
                base,
                idx_first_unittest_commit,
                idx_first_pytest_commit,
                idx_last_unittest_commit
            )
            base.update(data)
            return (base, author_infos)

        if self.__is_ongoing_repository(idx_first_unittest_commit, idx_first_pytest_commit):
            author_infos = CustomCommit.characterize_authors(self.allCommits, idx_first_pytest_commit, self.amount_total_commits - 1)
            data = self.__build_ongoing_repository_data(base, idx_first_unittest_commit, idx_first_pytest_commit)
            base.update(data)
            return (base, author_infos)

        if self.__gave_up_migration(idx_first_unittest_commit, idx_first_pytest_commit):
            author_infos = CustomCommit.characterize_authors(self.allCommits)
            data = self.__build_failed_to_migrate_repository_data(idx_first_unittest_commit, idx_first_pytest_commit)
            base.update(data)
            return (base, author_infos)

        data = self.__build_unknown_repository_data(idx_first_unittest_commit, idx_first_pytest_commit)
        author_infos = CustomCommit.characterize_authors(self.allCommits)
        base.update(data)
        return (base, author_infos)

    def __initial_state(self):
        commit_base_url = self.repo_url + '/commit/'
        number_of_authors_names, number_of_authors_emails = CustomCommit.get_total_count_authors(self.allCommits)

        return {
            'REPOSITORY_NAME': self.project_name,
            'REPOSITORY_LINK': self.repo_url,

            'NOC': self.amount_total_commits,

            'NOD': 0,
            'OCM': False,
            'NOA (name)': number_of_authors_names,
            'NOMA (name)': 0,
            "NOMAP (name)": 0,
            'NOA (email)': number_of_authors_emails,
            'NOMA (email)': 0,
            "NOMAP (email)": 0,
            "NOA email - name": number_of_authors_emails - number_of_authors_names,
            "PBU": False,

            'NOF': self.currentDefaultBranch.count_files(),
            'NOF_UNITTEST': self.currentDefaultBranch.nof_unittest,
            'NOF_PYTEST': self.currentDefaultBranch.nof_pytest,
            'NOF_BOTH': self.currentDefaultBranch.nof_both,

            'FC_UNITTEST': self.unittest_occurrences.first.commit['commit_hash'] if self.unittest_occurrences.has_first_occurrence() else None,
            'FC_PYTEST': self.pytest_occurrences.first.commit['commit_hash'] if self.pytest_occurrences.has_first_occurrence() else None,
            'FC_UNITTEST_LINK': commit_base_url + self.unittest_occurrences.first.commit['commit_hash'] if self.unittest_occurrences.has_first_occurrence() else None,
            'FC_PYTEST_LINK': commit_base_url + self.pytest_occurrences.first.commit['commit_hash'] if self.pytest_occurrences.has_first_occurrence() else None,

            'LC_UNITTEST': self.unittest_occurrences.last.commit['commit_hash'] if self.unittest_occurrences.has_last_occurrence() else None,
            'LC_PYTEST': self.pytest_occurrences.last.commit['commit_hash'] if self.pytest_occurrences.has_last_occurrence() else None,
            'LC_UNITTEST_LINK': commit_base_url + self.unittest_occurrences.last.commit['commit_hash'] if self.unittest_occurrences.has_last_occurrence() else None,
            'LC_PYTEST_LINK': commit_base_url + self.pytest_occurrences.last.commit['commit_hash'] if self.pytest_occurrences.has_last_occurrence() else None,
        }

    def __is_pytest_repository(self):
        return (not self.unittest_occurrences.has_first_occurrence()
                and self.pytest_occurrences.has_first_occurrence())

    def __is_unittest_repository(self):
        return (not self.pytest_occurrences.has_first_occurrence()
                and self.unittest_occurrences.has_first_occurrence())

    def __is_not_pytest_neither_unittest(self):
        return (not self.pytest_occurrences.has_first_occurrence()
                and not self.unittest_occurrences.has_first_occurrence())

    def __is_migrated_repository(self, idx_first_unittest_commit, idx_first_pytest_commit):
        return (self.unittest_occurrences.has_first_occurrence()
                and self.pytest_occurrences.has_first_occurrence()
                and (idx_first_unittest_commit <= idx_first_pytest_commit)
                and (self.currentDefaultBranch.usesPytest and not self.currentDefaultBranch.usesUnittest))

    def __is_ongoing_repository(self, idx_first_unittest_commit, idx_first_pytest_commit):
        return (self.unittest_occurrences.has_first_occurrence()
                and self.pytest_occurrences.has_first_occurrence()
                and (idx_first_unittest_commit <= idx_first_pytest_commit)
                and (self.currentDefaultBranch.usesPytest and self.currentDefaultBranch.usesUnittest))

    def __gave_up_migration(self, idx_first_unittest_commit, idx_first_pytest_commit):
        # started with unittest, added reference to pytest and then removed it.
        return (self.unittest_occurrences.has_first_occurrence()
                and self.pytest_occurrences.has_first_occurrence()
                and (idx_first_unittest_commit <= idx_first_pytest_commit)
                and (not self.currentDefaultBranch.usesPytest and self.currentDefaultBranch.usesUnittest))

    def __build_pytest_repository_data(self):
        data = {
            'CATEGORY': 'pytest',
            'NOC_UNITTEST': 0,
            'NOC_PYTEST': self.amount_total_commits,
            'NOC_BOTH': 0
        }
        return data

    def __build_unittest_repository_data(self):
        data = {
            'CATEGORY': 'unittest',
            'NOC_UNITTEST': self.amount_total_commits,
            'NOC_PYTEST': 0,
            'NOC_BOTH': 0
        }
        return data

    def __build_not_pytest_neither_unittest_data(self):
        data = {
            'CATEGORY': 'unknown',
            'NOC_UNITTEST': 0,
            'NOC_PYTEST': 0,
            'NOC_BOTH': 0,
        }
        return data

    def __build_migrated_repository_data(self, base, idx_first_unittest_commit, idx_first_pytest_commit, idx_last_unittest_commit):
        number_of_migration_authors_names, number_of_migration_authors_emails = \
            CustomCommit.get_migration_authors_count_between(self.allCommits, idx_first_pytest_commit, idx_last_unittest_commit)

        timedelta = self.unittest_occurrences.last.commit["date"] - \
            self.pytest_occurrences.first.commit["date"]

        data = {
            'CATEGORY': 'migrated',
            'NOC_UNITTEST': idx_last_unittest_commit - idx_first_unittest_commit,
            'NOC_PYTEST': self.amount_total_commits - idx_first_pytest_commit,
            'NOC_BOTH': idx_last_unittest_commit - idx_first_pytest_commit,
            'OCM': True if idx_last_unittest_commit == idx_first_pytest_commit else False,
            'NOD': timedelta.days,
            'NOMA (name)': number_of_migration_authors_names,
            "NOMAP (name)": round(number_of_migration_authors_names / base["NOA (name)"] * 100, 2),
            'NOMA (email)': number_of_migration_authors_emails,
            "NOMAP (email)": round(number_of_migration_authors_emails / base["NOA (email)"] * 100, 2)
        }
        return data

    def __build_ongoing_repository_data(self, base, idx_first_unittest_commit, idx_first_pytest_commit):
        number_of_migration_authors_names, number_of_migration_authors_emails = \
            CustomCommit.get_migration_authors_count_between(self.allCommits, idx_first_pytest_commit, self.amount_total_commits - 1)

        timedelta = datetime.now(timezone.utc) - \
            self.pytest_occurrences.first.commit["date"]

        data = {
            'CATEGORY': 'ongoing',
            'NOC_UNITTEST': self.amount_total_commits - idx_first_unittest_commit,
            'NOC_PYTEST': self.amount_total_commits - idx_first_pytest_commit,
            'NOC_BOTH': self.amount_total_commits - idx_first_pytest_commit,
            'NOD': timedelta.days,
            'NOMA (name)': number_of_migration_authors_names,
            "NOMAP (name)": round(number_of_migration_authors_names / base["NOA (name)"] * 100, 2),
            'NOMA (email)': number_of_migration_authors_emails,
            "NOMAP (email)": round(number_of_migration_authors_emails / base["NOA (email)"] * 100, 2)
        }
        return data

    def __build_failed_to_migrate_repository_data(self, idx_first_unittest_commit, idx_first_pytest_commit):
        idx_last_pytest_commit = CustomCommit.indexOf(
            self.allCommits, self.pytest_occurrences.last.commit["commit_hash"])

        data = {
            'CATEGORY': 'unittest',
            'NOC_UNITTEST': self.amount_total_commits - idx_first_unittest_commit,
            'NOC_PYTEST': idx_last_pytest_commit - idx_first_pytest_commit,
            'NOC_BOTH': idx_last_pytest_commit - idx_first_pytest_commit,
        }
        return data

    def __build_unknown_repository_data(self, idx_first_unittest_commit, idx_first_pytest_commit):
        pytest_before_unittest = idx_first_unittest_commit > idx_first_pytest_commit
        data = {
            'CATEGORY': 'unknown',
            'PBU': pytest_before_unittest,
            'NOC_UNITTEST': self.amount_total_commits - idx_first_unittest_commit,
            'NOC_PYTEST': self.amount_total_commits - idx_first_pytest_commit,
            'NOC_BOTH': self.amount_total_commits - idx_first_unittest_commit if pytest_before_unittest else 0,
        }
        return data
