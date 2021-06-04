from io_utils.input import InputUtil as inUtil
from io_utils.output import OutputUtil as outUtil
from analyzers.analyzer import Analyzer
from report.report import Report
from report.column_names import *
import sys
from datetime import datetime



def main(argv):
	input_file = inUtil.parse_command_line_arguments(argv)
	urls = inUtil.urls_from_input(input_file)

	dt_string = datetime.now().strftime("%d-%m-%Y_%H%M%S")
	out_dir = "out" + dt_string

	outUtil.create_out_path(out_dir)
	report = Report()

	dt_string = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
	print("Time marker #1", dt_string)
	for url in urls:
		analyzer = Analyzer(url, out_dir)
		data = analyzer.process_and_classify()
		report.add(data)
		print("This is a {} repository\n".format(data['CATEGORY']))


	print("Generating final reports...")
	columns = repository_columns()
	outUtil.output_as_csv("metrics_per_category", report.metrics_per_category, columns, filepath=out_dir)

	columns = aggregated_columns()
	report.process_aggregated()
	outUtil.output_as_csv("aggregated_metrics", report.aggregated_metrics, columns, filepath=out_dir)

	print("Done!")

if __name__ == "__main__":
	main(sys.argv[1:])
