__author__ = 'nico'
from urllib import quote_plus
from ..CustomUtils import get_current_time, get_random_str
import os
import glob
import logging

logger = logging.getLogger("ScreenUtils")
duplications = {}


def resolve_path(path=".", filename="screenshot.png", driver=None):
    if driver is not None:
        if "chrome" in driver.name: dname = "chrome"
        if "firefox" in driver.name: dname = "firefox"
        if "internet explorer" in driver.name: dname = "iexplorer"
        if "phantomjs" in driver.name: dname = "phantomjs"
        currurl = quote_plus(driver.current_url)
    else:
        dname = currurl = "undef"

    path = resolve_variable_names(path, dname, currurl)
    filename = resolve_variable_names(filename, dname, currurl)

    extension = filename[filename.index("."):]
    filename = filename.replace(extension, "")

    # Ensure a OS dependant separator at the end of the path
    if path[-1] not in ["/", "\\"]:
        path = path + os.sep

    if not os.path.exists(path):
        os.makedirs(path)
        logger.debug("Created folder: " + path)

    # ------------------------------------
    curr_duplicate = get_duplicates_amount(path, filename, extension)

    if curr_duplicate > 0:
        duplications[path + filename + extension] = curr_duplicate + 1

    f_index = ""
    logger.debug("Duplicates register:")
    logger.debug(duplications)
    if (path + filename + extension) in duplications:
        f_index = "_" + str(duplications[path + filename + extension])
        logger.info("Avoided image overwrite. New image path is: %s" % (path + filename + f_index + extension))
    # ------------------------------------

    final_path = path + filename + f_index + extension
    logger.debug("Saving screenshot: %s" % final_path)
    return final_path


def resolve_variable_names(path, dname="", currurl=""):
    # $hash is replaced after file writing
    return path.replace("$browser", dname)\
        .replace("$date", get_current_time())\
        .replace("$url", currurl)\
        .replace("$random", get_random_str())


def get_duplicates_amount(path, filename, extension):
    if extension is None: extension = ""
    dupes = glob.glob(path + filename + "_*" + extension)
    if len(dupes) > 0:
        logger.debug("Previous duplicates:")
        logger.debug(dupes)
        return get_max_duplicate(path, filename, extension)
    if os.path.isfile(path + filename + extension):
        logger.debug("File already exists.")
        return 1
    logger.debug("No previous file found. No overwrite risk.")
    return 0


def get_max_duplicate(path, filename, extension):
    # dupes_filenames = []
    nums = []
    # TODO: If the filename has a "_" in the name, it fails when there's a dupe already
    dupes = glob.glob(path + filename + '_*' + extension)
    for d in dupes:
    #    fname = d[d.rfind(os.sep)+1:]
    #    dupes_filenames.append(fname)
        # Here be dragons:
        # If it happens to fail, uncomment the rest and live a happy life
        nums.append(int(str(d[d.rfind(os.sep)+1:])[str(d[d.rfind(os.sep)+1:]).index("_")+1:str(d[d.rfind(os.sep)+1:]).rfind(".")]))
    #for f in dupes_filenames:
    #    fname_id = int(f[f.index("_")+1:f.rfind(".")])
    #    nums.append(fname_id)
    logger.debug("Numbers found:")
    logger.debug(nums)
    logger.debug("Highest duplicate found: " + str(max(nums)))
    return max(nums)


def remove_scrollbar(img):
    logger.error("Scrollbar removing is not implemented yet.")
    raise NotImplementedError
    # TODO: Implement me