from io_utils.input import *
from io_utils.output import *
from analyzers.commits_analyzer import CommitsAnalyzer
from analyzers.repository_analyzer import RepositoryAnalyzer


def main(argv):
	input_file = parse_command_line_arguments(argv)
	urls = urls_from_input(input_file)
	clear_out_path()

	for url in urls:
		analyzer = CommitsAnalyzer(url)
		analyzer.process_commits()
		analyzer.process_metrics()

		currentDefaultBranch = RepositoryAnalyzer(url)
		currentDefaultBranch.search_frameworks()
		analyzer.metrics.print_default()

		if (analyzer.unittest_occurrences.has_first_occurrence() \
			and currentDefaultBranch.usesPytest() and not currentDefaultBranch.usesUnittest()
			):
			print("This repo was migrated")
			analyzer.metrics.print_migration_percentage()
		elif currentDefaultBranch.usesPytest() and currentDefaultBranch.usesUnittest():
			print("This repo uses both frameworks")
		elif currentDefaultBranch.usesPytest() \
			and not analyzer.unittest_occurrences.has_first_occurrence():
			print("This is a pytest repository since day one.")
		elif currentDefaultBranch.usesUnittest() \
			and not analyzer.pytest_occurrences.has_first_occurrence():
			print("This is a unittest repository since day one.")
		else:
			print("Oops. I don't know about this repository.")
			print(currentDefaultBranch.usesPytest(), currentDefaultBranch.usesUnittest())

		# print to file
		fullpath = make_repository_out_path(analyzer.project_name)

		# if(repo.unittest_first_occurrence != {}):
		filename = fullpath + "unittest_first_addition.py"
		create_file_from_source_code(filename, analyzer.unittest_occurrences.first)

		# if(repo.unittest_last_occurrence != {}):
		filename = fullpath + "unittest_last_removal.py"
		create_file_from_source_code(filename, analyzer.unittest_occurrences.last)

		# if(repo.pytest_first_occurrence != {}):
		filename = fullpath + "pytest_first_addition.py"
		create_file_from_source_code(filename, analyzer.pytest_occurrences.first)

		# if(repo.pytest_last_occurrence != {}):
		filename = fullpath + "pytest_last_removal.py"
		create_file_from_source_code(filename, analyzer.pytest_occurrences.last)

if __name__ == "__main__":
	main(sys.argv[1:])
