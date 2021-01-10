from pydriller import RepositoryMining

print("\n")
print("Remote repository")
for commit in RepositoryMining("https://github.com/pallets/flask", only_in_branch="master", only_no_merge=True).traverse_commits():
    print("Project {}, commit {}, author {}".format(commit.project_name, commit.hash, commit.author.name))
    for modification in commit.modifications:
        print('\tAuthor {} modified {}'.format(commit.author.name, modification.new_path))

print("\n")
print("Metrics")
for commit in RepositoryMining("https://github.com/liviaab/backend-crawler").traverse_commits():
    for mod in commit.modifications:
        if(mod.complexity != None or len(mod.methods) != 0 or mod.nloc != None or mod.token_count != None ):
            print('{} \t has Cyclomatic Complexity of {},  it contains {} methods, {} lines of code and {} tokens'.format(
                  mod.filename, mod.complexity, len(mod.methods), mod.nloc, mod.token_count))

print("\n")
print("Single Commit")
for commit in RepositoryMining("https://github.com/pallets/flask", single="b724832872ae4b4cd4b5f61c153eae39f1c3b213").traverse_commits():
    print("Project {}, commit {}, author {}".format(commit.project_name, commit.hash, commit.author.name))
    for modification in commit.modifications:
        print('\tModified file: {}'.format(modification.new_path))

        if(modification.source_code != None):
            print('\tCode\n{}'.format(modification.source_code))
