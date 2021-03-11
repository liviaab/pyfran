import os
import json

def make_repository_out_path(repo_name):
    if not os.path.exists("out"):
        os.makedirs("out")

    if not os.path.exists("out/" + repo_name):
        os.makedirs("out/" + repo_name)

    return "out/" + repo_name + "/"

def create_file_from_source_code(filename, info_dict):
    print("create_file_from_source_code", filename)
    with open(filename,"w") as f:
        f.write(json.dumps(info_dict))
