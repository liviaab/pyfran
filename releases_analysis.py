import sys
import os
from datetime import datetime
import csv

from io_utils.input import InputUtil as inUtil
from io_utils.output import OutputUtil as outUtil
from analyzers.checkouts_analyzer import CheckoutsAnalyzer
from report.column_names import *


def main(argv):
  input_folder = inUtil.parse_checkout_commant_line_arguments(argv)

  for root, dirs, files in os.walk(input_folder):
    for file in files:
      if file.endswith("_commit.csv"):
        filepath = os.path.join(root, file)

        with open(filepath, newline='') as csvfile:
          print("Time marker 0 - repo {}".format(file))
          allcommits = list(csv.DictReader(csvfile))

          repo_url = allcommits[1]["commit_link"].split('/commit')[0]
          project_name = repo_url.split('/')[-1]
          print("Time marker #1 - {}\n{} - Process files from each checkout".format(repo_url, datetime.now().strftime("%d/%m/%Y %H:%M:%S")))
          # Clone the repo and visit each checkout to get information
          # about tests through time
          apis_info = CheckoutsAnalyzer(repo_url).process_checkouts(allcommits)

          print("Time marker #2 - create csv with APIs information", datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
          columns = api_columns()
          outUtil.output_list_as_csv(project_name+"_api", apis_info, columns, input_folder)
          print("Time marker #3 - done", datetime.now().strftime("%d/%m/%Y %H:%M:%S"))



  print("Done!")

if __name__ == "__main__":
  main(sys.argv[1:])
