from datetime import datetime, timezone

from analyzers.repository_analyzer import RepositoryAnalyzer
from analyzers.custom_commit import CustomCommit

class MainClassifier:
    def __init__(self, repo_url):
        self.repo_url = repo_url
        self.project_name = repo_url.split('/')[-1]
        pass

    def classify_and_process_metrics(self, allCommits, unittest_occurrences, pytest_occurrences):
        """
            classes: unittest | pytest | ongoing | migrated | unknown
        """

        currentDefaultBranch = RepositoryAnalyzer(self.repo_url)
        currentDefaultBranch.search_frameworks()

        commit_base_url = self.repo_url + '/commit/'

        amount_total_commits = len(allCommits)
        author_infos = []
        number_of_authors_names, number_of_authors_emails  = CustomCommit.get_total_count_authors(allCommits)

        base = {
            'REPOSITORY_NAME': self.project_name,
            'REPOSITORY_LINK': self.repo_url,
            
            'NOC': amount_total_commits,

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

            'NOF': currentDefaultBranch.count_files(),
            'NOF_UNITTEST': currentDefaultBranch.nof_unittest,
            'NOF_PYTEST': currentDefaultBranch.nof_pytest,
            'NOF_BOTH': currentDefaultBranch.nof_both,

            'FC_UNITTEST': unittest_occurrences.first.commit['commit_hash'] if unittest_occurrences.has_first_occurrence() else None,
            'FC_PYTEST': pytest_occurrences.first.commit['commit_hash'] if pytest_occurrences.has_first_occurrence() else None,
            'FC_UNITTEST_LINK': commit_base_url + unittest_occurrences.first.commit['commit_hash'] if unittest_occurrences.has_first_occurrence() else None,
            'FC_PYTEST_LINK': commit_base_url + pytest_occurrences.first.commit['commit_hash'] if pytest_occurrences.has_first_occurrence() else None,

            'LC_UNITTEST': unittest_occurrences.last.commit['commit_hash'] if unittest_occurrences.has_last_occurrence() else None,
            'LC_PYTEST': pytest_occurrences.last.commit['commit_hash'] if pytest_occurrences.has_last_occurrence() else None,
            'LC_UNITTEST_LINK': commit_base_url + unittest_occurrences.last.commit['commit_hash'] if unittest_occurrences.has_last_occurrence() else None,
            'LC_PYTEST_LINK': commit_base_url + pytest_occurrences.last.commit['commit_hash'] if pytest_occurrences.has_last_occurrence() else None,
        }

        if not unittest_occurrences.has_first_occurrence() \
            and pytest_occurrences.has_first_occurrence():
            author_infos = CustomCommit.characterize_authors(allCommits, amount_total_commits + 1, amount_total_commits + 1)
            data = {
                'CATEGORY': 'pytest',
                'NOC_UNITTEST': 0,
                'NOC_PYTEST': amount_total_commits,
                'NOC_BOTH': 0
            }
            base.update(data)
            return (base, author_infos)

        if not pytest_occurrences.has_first_occurrence() \
            and unittest_occurrences.has_first_occurrence():
            author_infos = CustomCommit.characterize_authors(allCommits, amount_total_commits + 1, amount_total_commits + 1)

            data = {
                'CATEGORY': 'unittest',
                'NOC_UNITTEST': amount_total_commits,
                'NOC_PYTEST': 0,
                'NOC_BOTH': 0
            }
            base.update(data)
            return (base, author_infos)

        if not pytest_occurrences.has_first_occurrence() \
            and not unittest_occurrences.has_first_occurrence():
            author_infos = CustomCommit.characterize_authors(allCommits, amount_total_commits + 1, amount_total_commits + 1)

            data = {
                'CATEGORY': 'unknown',
                'NOC_UNITTEST': 0,
                'NOC_PYTEST': 0,
                'NOC_BOTH': 0,
            }
            base.update(data)
            return (base, author_infos)

        idx_first_unittest_commit = CustomCommit.indexOf(allCommits, unittest_occurrences.first.commit["commit_hash"])
        idx_first_pytest_commit = CustomCommit.indexOf(allCommits, pytest_occurrences.first.commit["commit_hash"])

        if (unittest_occurrences.has_first_occurrence() and \
            pytest_occurrences.has_first_occurrence()) and \
            idx_first_unittest_commit <= idx_first_pytest_commit:

            if(currentDefaultBranch.usesPytest and not currentDefaultBranch.usesUnittest):
                idx_last_unittest_commit = CustomCommit.indexOf(allCommits, unittest_occurrences.last.commit["commit_hash"])
                number_of_migration_authors_names, number_of_migration_authors_emails = \
                    CustomCommit.get_authors_count_between(allCommits, idx_first_pytest_commit, idx_last_unittest_commit)
                timedelta = unittest_occurrences.last.commit["date"] - pytest_occurrences.first.commit["date"]

                author_infos = CustomCommit.characterize_authors(allCommits, idx_first_pytest_commit, idx_last_unittest_commit)
                data = {
                    'CATEGORY': 'migrated',
                    'NOC_UNITTEST': idx_last_unittest_commit - idx_first_unittest_commit,
                    'NOC_PYTEST': amount_total_commits - idx_first_pytest_commit,
                    'NOC_BOTH': idx_last_unittest_commit - idx_first_pytest_commit,
                    'OCM': True if idx_last_unittest_commit == idx_first_pytest_commit else False,
                    'NOD': timedelta.days,
                    'NOMA (name)': number_of_migration_authors_names,
                    "NOMAP (name)": round(number_of_migration_authors_names / base["NOA (name)"]* 100, 2),
                    'NOMA (email)': number_of_migration_authors_emails,
                    "NOMAP (email)": round(number_of_migration_authors_emails / base["NOA (email)"]* 100, 2)
                }
                base.update(data)
                return (base, author_infos)

            if(currentDefaultBranch.usesPytest and currentDefaultBranch.usesUnittest):
                number_of_migration_authors_names, number_of_migration_authors_emails = \
                    CustomCommit.get_authors_count_between(allCommits, idx_first_pytest_commit, amount_total_commits - 1)

                timedelta = datetime.now(timezone.utc) - pytest_occurrences.first.commit["date"]

                author_infos = CustomCommit.characterize_authors(allCommits, idx_first_pytest_commit, amount_total_commits -1)
                data = {
                    'CATEGORY': 'ongoing',
                    'NOC_UNITTEST': amount_total_commits - idx_first_unittest_commit,
                    'NOC_PYTEST': amount_total_commits - idx_first_pytest_commit,
                    'NOC_BOTH': amount_total_commits - idx_first_pytest_commit,
                    'NOD': timedelta.days,
                    'NOMA (name)': number_of_migration_authors_names,
                    "NOMAP (name)": round(number_of_migration_authors_names / base["NOA (name)"] * 100, 2),
                    'NOMA (email)': number_of_migration_authors_emails,
                    "NOMAP (email)": round(number_of_migration_authors_emails / base["NOA (email)"]* 100, 2)
                }
                base.update(data)
                return (base, author_infos)

        author_infos = CustomCommit.characterize_authors(allCommits, amount_total_commits + 1, amount_total_commits + 1)
        pbu = idx_first_unittest_commit > idx_first_pytest_commit
        data = {
            'CATEGORY': 'unknown',
            'PBU': pbu,
            'NOC_UNITTEST': amount_total_commits - idx_first_unittest_commit,
            'NOC_PYTEST': amount_total_commits - idx_first_pytest_commit,
            'NOC_BOTH': amount_total_commits - idx_first_unittest_commit if pbu else 0,
        }
    
        base.update(data)

        return (base, author_infos)