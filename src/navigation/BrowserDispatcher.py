from selenium import webdriver
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
import sys, logging

# ----- Default values -----

logger = logging.getLogger("obs.brDispatcher")
binaries = {"firefox": None, "chromedriver": None, "phantomjs": None, "iexplore": None}  # Overriden with config.json
drivers = []  # Module attribute. Keeps track of all opened browsers.

# --------------------
# ----- Browsers -----


def get_browser(name, binaries_cfg=None):
    global binaries
    binaries = binaries_cfg
    logger.debug("Binaries used: ")
    logger.debug(binaries)
    if "ff" in name or "firefox" in name:
        return get_firefox()
    elif "chrome" in name or "google chrome" in name:
        return get_chrome()
    elif "iexplore" in name or "internet explorer" in name or "ie" in name:
        return get_internet_explorer()
    elif "phantom" in name or "phantomjs" in name:
        return get_phantomjs()
    else:
        logger.error("Requested browser not recognized: " + str(name))
        exit(1)


def get_firefox():
    binary = FirefoxBinary(binaries.get("firefox"))
    d = webdriver.Firefox() if binary in (None, False, "") else webdriver.Firefox(firefox_binary=binary)
    _prepareDriver(d)
    return d


def get_chrome():
    binary = binaries.get("chromedriver")
    d = webdriver.Chrome() if binary in (None, False) else webdriver.Chrome(binary)
    _prepareDriver(d)
    return d


def get_internet_explorer():
    if "win" not in sys.platform:
        logger.warn("Internet Explorer is not available in non-Windows platforms, obviously.")
        return -1
    d = webdriver.Ie()
    _prepareDriver(d)
    return d


def get_phantomjs():
    binary = binaries.get("phantomjs")
    #d = webdriver.PhantomJS(executable_path=binary)
    d = webdriver.PhantomJS() if binary in (None, False, "") else webdriver.PhantomJS(executable_path=binary)
    _prepareDriver(d)
    return d

# ------------------------
# ----- Release all! -----


def get_all():
    browsers = [get_firefox(), get_chrome(), get_internet_explorer(), get_phantomjs()]
    [_prepareDriver(br) for br in browsers if br != -1]
    try:
        browsers.remove(-1)
    except ValueError:
        pass
    return browsers


def kill_all(_logger=None, reason=None):
    if _logger is not None and reason is not None:
        _logger(reason)
    [each.quit() for each in drivers]

# --------------------------------------------
# ----- Misc preparations applied to all -----


def _prepareDriver(drv):
    drv.set_window_position(0, 0)
    drivers.append(drv)
    pass
