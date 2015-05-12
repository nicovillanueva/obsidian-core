import argparse, logging
import sys
parser = argparse.ArgumentParser(add_help=False, description="Create and archive screenshots showing the current state of N pages.")

modes_group = parser.add_argument_group("Run modes")
modes_group.add_argument('--capture', action='store_true', help='Capture and archive the screenshots defined in the input file')
modes_group.add_argument('--compare', action='store_true', help='Compare the screenshots described in the input file')

options_group = parser.add_argument_group("Options")
options_group.add_argument('-i', '--input', help='Path to the JSON file that feeds the parameters to the test')
options_group.add_argument('-c', '--config-file', help='Override the default configuration JSON file. Default: ./config.json')
options_group.add_argument('-t', '--make-templates', action='store_true', help='Create (OR OVERWRITE) both an input.json and config.json example files')
options_group.add_argument('-h', '--help', action='help', help='Show this help message and exit')

# -----

import src.LoggerSetup as ls
ls.set_up_logging()

# -----

args = parser.parse_args()

cfgfile = args.config_file if args.config_file is not None else 'config.json'

if args.input is None:
    logging.critical("Please provide an input file.\
 Run with the '-t' argument to create default input and config files")
    sys.exit(1)

elif args.compare is True:
    import src.RunCompare as RunCompare
    RunCompare.run(args.input, cfgfile)

elif args.compare is False and args.capture is True:
    import src.RunCapture as RunCapture
    RunCapture.run(args.input, cfgfile)

elif args.make_templates is True:
    from shutil import copy2
    logging.info("Copying config.json and input.json")
    copy2('./skel/config_template.json', './config.json')
    copy2('./skel/input_capture_template.json', './input.json')

else:
    parser.parse_args(['--h'])  # show help if no parameters

# -----

logging.info("Exiting!")
