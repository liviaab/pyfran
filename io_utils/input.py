# from https://www.tutorialspoint.com/python3/python_command_line_arguments.htm
import sys
import getopt


def parse_command_line_arguments(argv):
	inputfile = ''
	outputfile = ''

	try:
		opts, _args = getopt.getopt(argv, "hi:o:", ["ifile=", "ofile="])
	except getopt.GetoptError:
		print('main.py -i <inputfile>.csv -o <outputfile>')
		sys.exit(2)

	for opt, arg in opts:
		if opt == '-h':
			print('main.py -i <inputfile>.csv -o <outputfile>')
			sys.exit()
		elif opt in ("-i", "--ifile"):
			inputfile = arg
		elif opt in ("-o", "--ofile"):
			outputfile = arg

	if not inputfile or not outputfile:
		print('usage: main.py -i <inputfile>.csv -o <outputfile>')
		sys.exit()
	if not inputfile.endswith('.csv'):
		print('usage: main.py -i <inputfile>.csv -o <outputfile>')
		print('\tThe input file must be .csv')
		sys.exit()

	print('Input file is ', inputfile)
	print('Output file is ', outputfile)

	return (inputfile, outputfile)

def urls_from_input(inputfile):
    urls = []
    with open(inputfile, 'r') as file:
        for line in file:
            values = line.split(',')
            urls.extend(values)

    return urls
