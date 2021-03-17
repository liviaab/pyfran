from io_utils.input import *
from io_utils.output import *
from analyzers.commits_analyzer import CommitsAnalyzer

def avg(list):
	return sum(list)/len(list)

def process_aggregated(metrics):
	print('\n\nProcessing aggregated metrics')
	print('Unit of measument: number of commits')
	print()
	if len(metrics['unittest']) == 0:
		print('This batch does not have unittest only repositories')
	else:
		print('Unittest only repositories', len(metrics['unittest']))
		print('\tMax\tMin\tAvg')
		_max = max(metrics['unittest'])
		_min = min(metrics['unittest'])
		_avg = avg(metrics['unittest'])
		print('\t{}\t{}\t{}'.format( _max, _min, _avg))

	print()
	if len(metrics['pytest']) == 0:
		print('This batch does not have pytest only repositories')
	else:
		print('Pytest only repositories', len(metrics['pytest']))
		print('\tMax\tMin\tAvg')
		_max = max(metrics['pytest'])
		_min = min(metrics['pytest'])
		_avg = avg(metrics['pytest'])
		print('\t{}\t{}\t{}'.format( _max, _min, _avg))

	print()
	if len(metrics['ongoing']) == 0:
		print('This batch does not have pytest only repositories')
	else:
		print('Repositories with ongoing migration', len(metrics['ongoing']))
		print('Average of the amount of commits containing:')
		print('\tTotal\tBoth\tPytest\tUnittest\tPercentage ')
		total = avg([t for t, p, u, b in metrics['ongoing']])
		both = avg([b for t, p, u, b in metrics['ongoing']])
		unittest = avg([p for t, p, u, b in metrics['ongoing']])
		pytest = avg([u for t, p, u, b in metrics['ongoing']])
		percentage = round(both / total * 100, 5)
		print('\t{}\t{}\t{}\t{}\t{}'.format(total, both, pytest, unittest, percentage))

	print()
	if len(metrics['migrated']) == 0:
		print('This batch does not have pytest only repositories')
	else:
		print('Migrated repositories', len(metrics['migrated']))
		print('Average of the amount of commits containing:')
		print('\tTotal\tBoth\tPytest\tUnittest\tPercentage ')
		total = avg([t for t, p, u, b in metrics['migrated']])
		both = avg([b for t, p, u, b in metrics['migrated']])
		unittest = avg([p for t, p, u, b in metrics['migrated']])
		pytest = avg([u for t, p, u, b in metrics['migrated']])
		percentage = round(both / total * 100, 5)
		print('\t{}\t{}\t{}\t{}\t{}'.format(total, both,  pytest, unittest, percentage))
	pass

def main(argv):
	input_file = parse_command_line_arguments(argv)
	urls = urls_from_input(input_file)
	aggregated_metrics = {
		'unittest': [],
		'pytest': [],
		'ongoing': [],
		'migrated': []
	}

	for url in urls:
		analyzer = CommitsAnalyzer(url)
		analyzer.process_commits()
		category, metrics = analyzer.classify_and_process_metrics()
		aggregated_metrics[category].append(metrics)

	process_aggregated(aggregated_metrics)



if __name__ == "__main__":
	main(sys.argv[1:])
