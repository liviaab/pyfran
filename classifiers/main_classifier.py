import functools
from datetime import datetime, timezone

from analyzers.repository_analyzer import RepositoryAnalyzer
from analyzers.custom_commit import CustomCommit


class MainClassifier:
    def __init__(self, repo_url, allCommits, unittest_occurrences, pytest_occurrences, migration_occurrences):
        self.repo_url = repo_url
        self.project_name = repo_url.split('/')[-1]
        self.allCommits = allCommits
        self.amount_total_commits = len(allCommits)
        self.currentDefaultBranch = RepositoryAnalyzer(self.repo_url)
        self.unittest_occurrences = unittest_occurrences
        self.pytest_occurrences = pytest_occurrences
        self.migration_occurrences = migration_occurrences
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

        idx_first_unittest_commit = self.unittest_occurrences.first.commit["commit_index"]

        idx_first_pytest_commit = self.pytest_occurrences.first.commit["commit_index"]

        if self.__is_migrated_repository(idx_first_unittest_commit, idx_first_pytest_commit):
            idx_last_unittest_commit = self.unittest_occurrences.last.commit["commit_index"]
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
            'Repository Name': self.project_name,
            'Repository Link': self.repo_url,

            'No. Total Commits': self.amount_total_commits,

            'Lifetime in days': self.calculate_lifetime(),
            'No. Days (between frameworks occurrence)': 0,
            'One Commit Migration?': False,
            'No. Authors (name)': number_of_authors_names,
            'No. Migration Authors (name)': 0,
            "Percentage of Migration Authors (name)": 0,
            'No. Authors (email)': number_of_authors_emails,
            'No. Migration Authors (email)': 0,
            "Percentage of Migration Authors (email)": 0,
            "No. Authors (email - name)": number_of_authors_emails - number_of_authors_names,
            "Pytest before Unittest?": False,

            'No. Files (current state)': self.currentDefaultBranch.count_files(),
            'No. Files with unittest': self.currentDefaultBranch.nof_unittest,
            'No. Files with pytest': self.currentDefaultBranch.nof_pytest,
            'No. Files with both': self.currentDefaultBranch.nof_both,


            '1st commit UNITTEST': self.unittest_occurrences.first.commit['commit_hash'] if self.unittest_occurrences.has_first_occurrence() else None,
            '1st commit PYTEST': self.pytest_occurrences.first.commit['commit_hash'] if self.pytest_occurrences.has_first_occurrence() else None,
            '1st commit UNITTEST_LINK': commit_base_url + self.unittest_occurrences.first.commit['commit_hash'] if self.unittest_occurrences.has_first_occurrence() else None,
            '1st commit PYTEST_LINK': commit_base_url + self.pytest_occurrences.first.commit['commit_hash'] if self.pytest_occurrences.has_first_occurrence() else None,

            'Last commit UNITTEST': self.unittest_occurrences.last.commit['commit_hash'] if self.unittest_occurrences.has_last_occurrence() else None,
            'Last commit PYTEST': self.pytest_occurrences.last.commit['commit_hash'] if self.pytest_occurrences.has_last_occurrence() else None,
            'Last commit UNITTEST_LINK': commit_base_url + self.unittest_occurrences.last.commit['commit_hash'] if self.unittest_occurrences.has_last_occurrence() else None,
            'Last commit PYTEST_LINK': commit_base_url + self.pytest_occurrences.last.commit['commit_hash'] if self.pytest_occurrences.has_last_occurrence() else None,

            'No. Days (between migration commits)': 0,
            'No. Migration commits': functools.reduce(lambda acc, commit: acc + 1 if commit['are_we_interested'] else acc, self.allCommits, 0),
            'No. Commits (between migration period)': 0,
            '1st migration commit': self.migration_occurrences.first.commit['commit_hash'] if self.migration_occurrences.has_first_occurrence() else None,
            '1st migration commit link': commit_base_url + self.migration_occurrences.first.commit['commit_hash'] if self.migration_occurrences.has_first_occurrence() else None,
            'Last migration commit': self.migration_occurrences.last.commit['commit_hash'] if self.migration_occurrences.has_last_occurrence() else None,
            'Last migration commit link': commit_base_url + self.migration_occurrences.last.commit['commit_hash'] if self.migration_occurrences.has_last_occurrence() else None,

        }

    def calculate_lifetime(self):
        commit = self.allCommits[0]
        if commit['commit_index'] != 0:
            raise RuntimeError('Error when calculating lifetime in days')

        timedelta = datetime.now(timezone.utc) - commit['date']
        return timedelta.days

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
            "No. Commits from 1st unittest occurrence": 0,
            "No. Commits from 1st pytest occurrence": self.amount_total_commits,

        }
        return data

    def __build_unittest_repository_data(self):
        data = {
            'CATEGORY': 'unittest',
            "No. Commits from 1st unittest occurrence": self.amount_total_commits,
            "No. Commits from 1st pytest occurrence": 0,
        }
        return data

    def __build_not_pytest_neither_unittest_data(self):
        data = {
            'CATEGORY': 'unknown',
            "No. Commits from 1st unittest occurrence": 0,
            "No. Commits from 1st pytest occurrence": 0,
        }
        return data

    def __build_migrated_repository_data(self, base, idx_first_unittest_commit, idx_first_pytest_commit, idx_last_unittest_commit):

        number_of_migration_authors_names, number_of_migration_authors_emails = \
            CustomCommit.get_migration_authors_count_between(self.allCommits, idx_first_pytest_commit, idx_last_unittest_commit)

        timedelta = self.unittest_occurrences.last.commit["date"] - \
            self.pytest_occurrences.first.commit["date"]

        data = {
            'CATEGORY': 'migrated',

            "No. Commits from 1st unittest occurrence": idx_last_unittest_commit - idx_first_unittest_commit,
            "No. Commits from 1st pytest occurrence": self.amount_total_commits - idx_first_pytest_commit,

            'No. Days (between frameworks occurrence)': timedelta.days,
            'No. Migration Authors (name)': number_of_migration_authors_names,
            'Percentage of Migration Authors (name)': round(number_of_migration_authors_names / base["No. Authors (name)"] * 100, 2),
            'No. Migration Authors (email)': number_of_migration_authors_emails,
            'Percentage of Migration Authors (email)': round(number_of_migration_authors_emails / base["No. Authors (email)"] * 100, 2),

            'One Commit Migration?': True if idx_last_unittest_commit == idx_first_pytest_commit else False,
            'No. Commits (between migration period)': \
                self.migration_occurrences.last.commit["commit_index"] - self.migration_occurrences.first.commit["commit_index"] + 1 \
                if self.migration_occurrences.has_first_occurrence() else None,
            'No. Days (between migration commits)': self.__commit_migration_delta_days() \
                if self.migration_occurrences.has_first_occurrence() else 0,
        }
        return data

    def __build_ongoing_repository_data(self, base, idx_first_unittest_commit, idx_first_pytest_commit):
        number_of_migration_authors_names, number_of_migration_authors_emails = \
            CustomCommit.get_migration_authors_count_between(self.allCommits, idx_first_pytest_commit, self.amount_total_commits - 1)

        timedelta = datetime.now(timezone.utc) - \
            self.pytest_occurrences.first.commit["date"]

        timedelta_migration = \
            datetime.now(timezone.utc) - self.migration_occurrences.first.commit["date"] \
            if self.migration_occurrences.has_first_occurrence() else None 

        data = {
            'CATEGORY': 'ongoing',

            "No. Commits from 1st unittest occurrence": self.amount_total_commits - idx_first_unittest_commit,
            "No. Commits from 1st pytest occurrence": self.amount_total_commits - idx_first_pytest_commit,

            'No. Days (between frameworks occurrence)': timedelta.days,
            'No. Migration Authors (name)': number_of_migration_authors_names,
            'Percentage of Migration Authors (name)': round(number_of_migration_authors_names / base["No. Authors (name)"] * 100, 2),
            'No. Migration Authors (email)': number_of_migration_authors_emails,
            'Percentage of Migration Authors (email)': round(number_of_migration_authors_emails / base["No. Authors (email)"] * 100, 2),
            'No. Commits (between migration period)': self.amount_total_commits - self.migration_occurrences.first.commit["commit_index"] \
                                                        if self.migration_occurrences.has_first_occurrence() else 0,
            'No. Days (between migration commits)': self.__commit_migration_delta_ongoing_days() \
                                                        if self.migration_occurrences.has_first_occurrence() else 0,
        }
        return data

    def __build_failed_to_migrate_repository_data(self, idx_first_unittest_commit, idx_first_pytest_commit):
        idx_last_pytest_commit = self.pytest_occurrences.last.commit["commit_index"]

        commits_between_migration = \
            (self.migration_occurrences.last.commit["commit_index"] - self.migration_occurrences.first.commit["commit_index"] + 1) \
            if self.migration_occurrences.has_first_occurrence() else 0

        commit_migration_delta_days = \
            self.__commit_migration_delta_days() if self.migration_occurrences.has_first_occurrence() else 0

        data = {
            'CATEGORY': 'unittest',
            "No. Commits from 1st unittest occurrence": self.amount_total_commits - idx_first_unittest_commit,
            "No. Commits from 1st pytest occurrence": idx_last_pytest_commit - idx_first_pytest_commit,
            'No. Commits (between migration period)': commits_between_migration,
            'No. Days (between migration commits)': commit_migration_delta_days,
        }
        return data

    def __build_unknown_repository_data(self, idx_first_unittest_commit, idx_first_pytest_commit):
        pytest_before_unittest = idx_first_unittest_commit > idx_first_pytest_commit

        data = {
            'CATEGORY': 'unknown',
            'Pytest before Unittest?': pytest_before_unittest,
            "No. Commits from 1st unittest occurrence": self.amount_total_commits - idx_first_unittest_commit,
            "No. Commits from 1st pytest occurrence": self.amount_total_commits - idx_first_pytest_commit,
        }
        return data

    def __commit_migration_delta_days(self):
        timedelta = self.migration_occurrences.last.commit["date"] - self.migration_occurrences.first.commit["date"]
        return timedelta.days

    def __commit_migration_delta_ongoing_days(self):
        timedelta = datetime.now(timezone.utc) - self.migration_occurrences.first.commit["date"]
        return timedelta.days
