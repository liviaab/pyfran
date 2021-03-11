from io_utils.input import *
from io_utils.output import *
from repository.repository import *


def main(argv):
	input_file = parse_command_line_arguments(argv)
	urls = urls_from_input(input_file)

	for url in urls:
		print(url)
		repo = Repository(url)
		repo.traverse_commits()
		fullpath = make_repository_out_path(
			repo.unittest_first_occurrence["project_name"] or \
			repo.pytest_first_occurrence["project_name"]
		)

		# if(repo.unittest_first_occurrence != {}):
		filename = fullpath + "unittest_first_occurrence.py"
		print(repo.unittest_first_occurrence)
		create_file_from_source_code(filename, repo.unittest_first_occurrence)

		# if(repo.unittest_last_occurrence != {}):
		filename = fullpath + "unittest_last_occurrence.py"
		print(repo.unittest_last_occurrence)
		create_file_from_source_code(filename, repo.unittest_last_occurrence)

		# if(repo.pytest_first_occurrence != {}):
		filename = fullpath + "pytest_first_occurrence.py"
		print(repo.pytest_first_occurrence)
		create_file_from_source_code(filename, repo.pytest_first_occurrence)

		# if(repo.pytest_last_occurrence != {}):
		filename = fullpath + "pytest_last_occurrence.py"
		print(repo.pytest_last_occurrence)
		create_file_from_source_code(filename, repo.pytest_last_occurrence)


if __name__ == "__main__":
	main(sys.argv[1:])
