from io_utils.input import *
from io_utils.output import *
from repository.repository import *

def main(argv):
	input_file, output_file = parse_command_line_arguments(argv)
	urls = urls_from_input(input_file)
	print(urls)

	for url in urls:
		repo = Repository(url)
		repo.traverse_commits()


if __name__ == "__main__":
	main(sys.argv[1:])
