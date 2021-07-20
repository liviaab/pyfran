# from https://www.tutorialspoint.com/python3/python_command_line_arguments.htm
import sys
import getopt
import os

class InputUtil:
	@classmethod
	def parse_command_line_arguments(cls, argv):
		inputfile = ''

		try:
			opts, _args = getopt.getopt(argv, "hi:o:", ["ifile="])
		except getopt.GetoptError:
			print('main.py -i <inputfile>.csv')
			sys.exit(2)

		for opt, arg in opts:
			if opt == '-h':
				print('main.py -i <inputfile>.csv')
				sys.exit()
			elif opt in ("-i", "--ifile"):
				inputfile = arg

		if not inputfile :
			print('usage: main.py -i <inputfile>.csv ')
			sys.exit()
		if not inputfile.endswith('.csv'):
			print('usage: main.py -i <inputfile>.csv')
			print('\tThe input file must be .csv')
			sys.exit()

		print('Input file is ', inputfile)

		return (inputfile)

	@classmethod
	def parse_checkout_commant_line_arguments(cls, argv):
		inputfolder = ''
		try:
			opts, _args = getopt.getopt(argv, "hi:", ["ifile="])
		except getopt.GetoptError:
			print('releases_analysis.py -i <inputfolder>')
			sys.exit(2)

		for opt, arg in opts:
			if opt == '-h':
				print('releases_analysis.py -i <inputfolder>')
				sys.exit()
			elif opt in ("-i", "--idir"):
				inputfolder = arg

		if not inputfolder:
			print('usage: releases_analysis.py -i <inputfolder>')
			sys.exit()
		if not os.path.isdir(inputfolder):
			print('usage: releases_analysis.py -i <inputfolder>')
			print('\tThe input folder must exist')
			sys.exit()

		print('Input folder is ', inputfolder)

		return (inputfolder)

	@classmethod
	def not_blank(cls, word):
		if (word == ''):
			return False

		return True

	@classmethod
	def urls_from_input(cls, inputfile):
		urls = []

		with open(inputfile, 'r') as file:
			for line in file:
				values = line.rstrip().replace(' ', '').split(",")
				values = filter(cls.not_blank, values)
				urls.extend(values)

		return urls
