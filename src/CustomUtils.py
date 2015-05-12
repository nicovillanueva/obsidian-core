__author__ = 'nico'
import random, string, datetime, time, logging, json, sys, os

logger = logging.getLogger("obs.Utils")


def get_random_str(amount=16):
    return "".join([random.choice(string.ascii_letters + string.digits) for _ in range(amount)])


def get_current_time():
    return datetime.datetime.fromtimestamp(time.time()).strftime('%d-%m-%Y_%Hh-%Mm')


def json_parse(jsonfile, expected_keys=None):
    try:
        with open(jsonfile, 'r') as jsondata:
            logger.debug("Loading file: " + str(jsonfile))
            data = json.load(jsondata)
        if expected_keys is not None and not validate_json(data, expected_keys):
            logger.critical("Expected values not found. Run with '-t' to make new templates.")
            logger.critical("Expected: " + str(expected_keys))
            sys.exit(3)
        logger.debug("Returning: " + str(data))
        return data
    except IOError:
        logger.critical("JSON file (%s) not found, yo" % jsonfile)
        sys.exit(1)
    except ValueError:
        logger.critical("The supplied JSON (%s) is not valid, yo" % jsonfile)
        sys.exit(2)


def validate_json(jsondata, expected_keys):
    k = jsondata.keys()
    return set(expected_keys).issubset(k)


def save_dict_to_json(dictdata, filename):
    filename = resolve_variable_names(filename)
    if not os.path.exists(os.path.dirname(filename)):
        os.makedirs(os.path.dirname(filename))
    with open(filename, 'w') as f:
        f.write(json.dumps(obj=dictdata, sort_keys=True, indent=4))


def resolve_variable_names(filename):
    from screenshots.ScreenshotterUtils import get_random_str, get_current_time
    return filename.replace("$date", get_current_time())\
        .replace("$random", get_random_str(8))