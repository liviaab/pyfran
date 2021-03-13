from io_utils.input import *
from io_utils.output import *
from commits_analyzer.commits_analyzer import CommitsAnalyzer


def main(argv):
	input_file = parse_command_line_arguments(argv)
	urls = urls_from_input(input_file)
	clear_out_path()

	for url in urls:
		analyzer = CommitsAnalyzer(url)
		analyzer.process_commits()

		fullpath = make_repository_out_path(analyzer.project_name)

		# if(repo.unittest_first_occurrence != {}):
		filename = fullpath + "unittest_first_occurrence.py"
		create_file_from_source_code(filename, analyzer.unittest_occurrences.first)

		# if(repo.unittest_last_occurrence != {}):
		filename = fullpath + "unittest_last_occurrence.py"
		create_file_from_source_code(filename, analyzer.unittest_occurrences.last)

		# if(repo.pytest_first_occurrence != {}):
		filename = fullpath + "pytest_first_occurrence.py"
		create_file_from_source_code(filename, analyzer.pytest_occurrences.first)

		# if(repo.pytest_last_occurrence != {}):
		filename = fullpath + "pytest_last_occurrence.py"
		create_file_from_source_code(filename, analyzer.pytest_occurrences.last)


if __name__ == "__main__":
	main(sys.argv[1:])
