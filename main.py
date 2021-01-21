from io_utils.input import *
from io_utils.output import *

def main(argv):
	input_file, output_file = parse_command_line_arguments(argv)
	print(input_file)
	print(output_file)



if __name__ == "__main__":
	main(sys.argv[1:])
