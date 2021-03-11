import os
# import json
from pprint import PrettyPrinter

def make_repository_out_path(repo_name):
    if not os.path.exists("out"):
        os.makedirs("out")

    if not os.path.exists("out/" + repo_name):
        os.makedirs("out/" + repo_name)

    return "out/" + repo_name + "/"

def create_file_from_source_code(filename, info_dict):
    pprinter = PrettyPrinter()
    with open(filename,"w") as f:
        f.write(pprinter.pformat(info_dict))
