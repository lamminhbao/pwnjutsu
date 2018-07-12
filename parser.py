import argparse
import logging

cmd_args = None

def argparser(main):
	parser = argparse.ArgumentParser()
	parser.add_argument("-v", "--verbose", help="print verbose log", 
						default = 0, action="count")
	parser.add_argument("-f", "--force", help="run anyway", action="store_true")
	parser.add_argument("-i", "--input", help="manual input", action="store_true")
	parser.add_argument("-o", "--output", help="print output", action="store_true")
	parser.add_argument("filepath", help="ELF file path")

	global cmd_args
	cmd_args = parser.parse_args()
	if cmd_args.verbose == 1:
		logging.basicConfig(level = logging.INFO)
	elif cmd_args.verbose >= 2:
		logging.basicConfig(level = logging.DEBUG)
	
	if cmd_args.filepath != '':
		main(cmd_args.filepath)