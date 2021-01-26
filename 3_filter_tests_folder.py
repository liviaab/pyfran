import re
from pydriller import RepositoryMining

pytest_first_occurrence = {}
pytest_last_occurrence = {}
unittest_first_occurrence = {}
unittest_last_occurrence = {}

print("\n")
print("Remote repository - Flask")
for commit in RepositoryMining("https://github.com/pallets/flask", only_in_branch="master", only_no_merge=True).traverse_commits():
    for modification in commit.modifications:
        # print('\t{} is a test file? {}'.format(modification.new_path, is_a_test_file(modification.new_path)))

        if is_a_test_file(modification.new_path):
            print("Commit {}, author {} ({})".format(commit.hash, commit.author.name, commit.author_date))
            uses_unittest = check_unittest(modification.source_code)
            uses_pytest = check_pytest(modification.source_code)

            if uses_pytest and uses_unittest:
                print('\tThe file: {} uses both frameworks'.format(modification.new_path))
            elif uses_pytest:
                print('\tThe file: {} uses both pytest'.format(modification.new_path))
            else:
                print('\tThe file: {} uses both unittest'.format(modification.new_path))

            if not unittest_first_occurrence and uses_unittest:
                unittest_first_occurrence = {
                    "file": modification.new_path,
                    "author": commit.author.name,
                    "date": commit.author_date,
                    "commit_hash": commit.hash,
                    "commit_message": commit.msg,
                }

            if uses_unittest:
                unittest_last_occurrence = {
                    "file": modification.new_path,
                    "author": commit.author.name,
                    "date": commit.author_date,
                    "commit_hash": commit.hash,
                    "commit_message": commit.msg,
                }

            if not pytest_first_occurrence and uses_pytest:
                pytest_first_occurrence = {
                    "file": modification.new_path,
                    "author": commit.author.name,
                    "date": commit.author_date,
                    "commit_hash": commit.hash,
                    "commit_message": commit.msg,
                }

            if uses_pytest:
                pytest_last_occurrence = {
                    "file": modification.new_path,
                    "author": commit.author.name,
                    "date": commit.author_date,
                    "commit_hash": commit.hash,
                    "commit_message": commit.msg,
                }



print("The first occurence of pytest was:")
print(pytest_first_occurrence)
print("The first occurence of unittest was:")
print(unittest_first_occurrence)
print("The last occurence of pytest was:")
print(pytest_last_occurrence)
print("The last occurence of unittest was:")
print(unittest_last_occurrence)
