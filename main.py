from io_utils.input import *
from io_utils.output import *
from analyzers.commits_analyzer import CommitsAnalyzer


def main(argv):
	input_file = parse_command_line_arguments(argv)
	urls = urls_from_input(input_file)

	for url in urls:
		analyzer = CommitsAnalyzer(url)
		analyzer.process_commits()
		analyzer.process_metrics()

if __name__ == "__main__":
	main(sys.argv[1:])
