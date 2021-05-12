from io_utils.input import InputUtil as inUtil
from io_utils.output import OutputUtil as outUtil
from analyzers.commits_analyzer import CommitsAnalyzer
from report.report import Report
import sys
from datetime import datetime

def repository_columns():
	return  [                
                "CATEGORY",
                "REPOSITORY_NAME",
                "REPOSITORY_LINK",
                "NOC",
                "NOC_UNITTEST",
                "NOC_PYTEST",
                "NOC_BOTH",
                "OCM",
                "NOD",
                "NOF",
                "NOF_UNITTEST",
                "NOF_PYTEST",
                "NOF_BOTH",
                "FC_UNITTEST",
                "FC_PYTEST",
                "FC_UNITTEST_LINK",
                "FC_PYTEST_LINK",
                "LC_UNITTEST",
                "LC_PYTEST",
                "LC_UNITTEST_LINK",
                "LC_PYTEST_LINK"
           ]

def aggregated_columns():
	return [
				'CATEGORY',
				'NOP',
				'NOC - MEAN',
				'NOC - MEDIAN',
				'NOC - MAX',
				'NOC - MIN',

				'NOC_UNITTEST - MEAN',
				'NOC_UNITTEST - MEDIAN',
				'NOC_UNITTEST - MAX',
				'NOC_UNITTEST - MIN',

				'NOC_PYTEST - MEAN',
				'NOC_PYTEST - MEDIAN',
				'NOC_PYTEST - MAX',
				'NOC_PYTEST - MIN',

				'NOC_BOTH - MEAN',
				'NOC_BOTH - MEDIAN',
				'NOC_BOTH - MAX',
				'NOC_BOTH - MIN',

				'NOF - MEAN',
				'NOF - MEDIAN',
				'NOF - MAX',
				'NOF - MIN',

				'NOF_UNITTEST - MEAN',
				'NOF_UNITTEST - MEDIAN',
				'NOF_UNITTEST - MAX',
				'NOF_UNITTEST - MIN',

				'NOF_PYTEST - MEAN',
				'NOF_PYTEST - MEDIAN',
				'NOF_PYTEST - MAX',
				'NOF_PYTEST - MIN',

				'NOF_BOTH - MEAN',
				'NOF_BOTH - MEDIAN',
				'NOF_BOTH - MAX',
				'NOF_BOTH - MIN',
		]

def main(argv):
	input_file = inUtil.parse_command_line_arguments(argv)
	urls = inUtil.urls_from_input(input_file)
	now = datetime.now()
	dt_string = now.strftime("%d-%m-%Y_%H%M%S")
	out_path = "out" + dt_string

	outUtil.create_out_path(out_path)
	report = Report()

	now = datetime.now()
	dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
	print("Time marker #1", dt_string)
	for url in urls:
		analyzer = CommitsAnalyzer(url)
		data = analyzer.process_and_classify()
		report.add(data)
		outUtil.output_to(data['REPOSITORY_NAME'], data, filepath=out_path)
		print("This is a {} repository\n".format(data['CATEGORY']))
		

	report.process_aggregated()
	print("Generating final reports...")
	columns = repository_columns()
	outUtil.output_as_csv("FINAL_metrics_per_category", report.metrics_per_category, columns, filepath=out_path)
	columns = aggregated_columns()
	outUtil.output_as_csv("FINAL_aggregated_metrics", report.aggregated_metrics, columns, filepath=out_path)
	print("Done!")

if __name__ == "__main__":
	main(sys.argv[1:])
