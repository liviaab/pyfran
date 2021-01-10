from pydriller import RepositoryMining

"""
    Returns the hashes of all commits in a repository
"""

print("\n")
print("Multiple local repositories")
urls = [
    "/Users/livia/Documents/github_pvt/vhd_v2",
    "/Users/livia/Documents/github_pvt/tdc-recife-2020"
]
for commit in RepositoryMining(urls).traverse_commits():
    print("Project {}, commit {}, date {}".format(
           commit.project_path, commit.hash, commit.author_date))

print("\n")
print("Remote repository")
for commit in RepositoryMining("https://github.com/pallets/flask", only_in_branch="master", only_no_merge=True).traverse_commits():
    print("Project {}, commit {}, author {}".format(
           commit.project_name, commit.hash, commit.author.name))
