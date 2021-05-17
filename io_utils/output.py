import os
import shutil
import csv
from pprint import PrettyPrinter
from datetime import datetime

DEFAULT_DIR_PATH = "out/"
DEFAULT_EXTENSION = '.csv'

class OutputUtil:
    @classmethod
    def create_out_path(cls, dir=DEFAULT_DIR_PATH):
        if not os.path.exists(dir):
            os.makedirs(dir)

        return

    @classmethod
    def output_to(cls, repo_name, data, extension=DEFAULT_EXTENSION, filepath=DEFAULT_DIR_PATH, depth=1):
        full_path = os.path.join(filepath, repo_name + extension)
        pprinter = PrettyPrinter(depth=depth)

        with open(full_path, "w") as f:
            f.write(pprinter.pformat(data))

        return

    @classmethod
    def output_as_csv(cls, filename, data, columns, filepath=DEFAULT_DIR_PATH):
        full_path = os.path.join(filepath, filename + DEFAULT_EXTENSION)

        with open(full_path, "w") as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=columns)
            writer.writeheader()

            for _category, repos in data.items():
                for repo in repos:
                    writer.writerow(repo)
        
        return

    @classmethod
    def output_list_as_csv(cls, filename, dataList, columns, filepath=DEFAULT_DIR_PATH):
        full_path = os.path.join(filepath, filename + DEFAULT_EXTENSION)

        with open(full_path, "w") as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=columns)
            writer.writeheader()

            for item in dataList:
                writer.writerow(item)

        return