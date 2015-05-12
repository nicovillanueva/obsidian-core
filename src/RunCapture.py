import json, logging, sys, datetime, time, itertools
import src.navigation.BrowserDispatcher as bd
from src.mailing.Mailer import Mailer
from src.navigation.BrowserArray import BrowserArray
from src.database.Screenshots_DB import Screenshots_DB
from CustomUtils import json_parse

logger = logging.getLogger('RunCapture')


def run(testparams, config):
    """
    Receive a JSON file with all parameters, and run away.
    Send mail report and store in DB if needed.
    """
    expected_keys = ["screenshots", "urls", "browsers", "window_sizes"]
    testdata = json_parse(testparams, expected_keys)
    cfgdata = json_parse(config)

    if not cfgdata.get("debug"):
        try:
            results = _main(testdata, cfgdata)
            logger.debug("Each screenshot info:")
            for each in results.get("screenshots"):
                logger.debug(each.to_string())
            logger.debug("All results:")
            logger.debug(results)
        except Exception, e:
            bd.kill_all(logger.critical, e)
            raise e
        #finally:
        #    bd.kill_all()
    else:
        results = _main(testdata, cfgdata)
        logger.debug("Each screenshot info:")
        for each in results.get("screenshots"):
            logger.debug(each.to_string())
        logger.debug("All results:")
        logger.debug(results)

    # TODO: Move mailing to obsidian-reporting
    """
    #
    # Disable mailing: Will move to obsidian-reporting
    #
    if "mail_reports" in testdata and len(testdata["mail_reports"]["destinations"]) > 0:
        smtp = cfgdata["smtp"]
        m = Mailer(smtp["host"], smtp["port"], smtp["user"], smtp["pass"], smtp["tls"], smtp["ehlo"])
        m.send_report(testdata["mail_reports"]["destinations"], results, testdata["mail_reports"]["images_width"])
    """
    # Store results in db
    if testdata.get("screenshots").get("store_in_db"):
        dbcheck = True if cfgdata.get("check_database_schema") else False
        db = Screenshots_DB(cfgdata.get("database_path"), safe=dbcheck)
        db.store_screenshots(results.get("screenshots"))


def _main(testdata, cfgdata):
    """
    Given a list of URLs to test, and some browsers to test in,
    enter each URL with each browser, take screenshots, and return a dict with
    the test run results.
    Date format is: YYYY-mm-dd HH:mm:ss

    Returns a dict: {test_start: <date>, test_end: <date>, screenshots:[<Screenshot entities>]}
    """

    sshots_entities = []

    start_time = datetime.datetime.fromtimestamp(time.time())

    barr = _build_browsers_array(testdata.get("browsers"), cfgdata.get("binaries"), cfgdata.get("timeouts"))

    for each in testdata.get("urls"):
        if each[0] == "#": continue  # Accept comments in URL list.

        # Load page
        logger.info("Capturing %s" % each)
        ignored_browsers = barr.get(each, testdata.get("cookies"))

        # Default to fullscreen if there are no window_sizes defined
        if "window_sizes" not in testdata or len(testdata.get("window_sizes")) <= 0:
            testdata["window_sizes"] = "fullscreen"

        # Resize and take each screenshot
        for size in testdata.get("window_sizes"):
            if size == "fullscreen":
                barr.maximize_window()
            else:
                wid, hei = size
                barr.set_window_size(wid, hei)
            s_path = testdata.get("screenshots").get("path")
            s_fname = testdata.get("screenshots").get("filename")
            screens = barr.save_screenshot(s_path, s_fname, ignored_browsers)
            sshots_entities.append(screens)  # sshots_entities => list of lists (each browser) of sshots

        # ---------

        logger.debug("Screenshots so far:")
        for eachgroup in sshots_entities:
            for each in eachgroup:
                logger.debug(each.path)

    barr.quit()

    # Flatten list
    sshots_entities = list(itertools.chain.from_iterable(sshots_entities))
    logger.debug("All screenshots: " + str([sshot.path for sshot in sshots_entities]))
    end_time = datetime.datetime.fromtimestamp(time.time())
    logger.info("DONE! The test took: " + str((end_time - start_time).seconds) + " seconds.")

    results = {"test_start": start_time.strftime('%Y-%m-%d %H:%M:%S'),
               "test_end": end_time.strftime('%Y-%m-%d %H:%M:%S'),
               "screenshots": sshots_entities
    }
    logger.debug("Final results: " + str(results))
    return results

def _build_browsers_array(requestedbrowsers, binaries=None, timeouts=None):
    browsers = []
    targetbrowsers = [br for br in requestedbrowsers if requestedbrowsers[br] == True]
    for br in targetbrowsers:
        spawned_browser = bd.get_browser(br, binaries, timeouts)
        if spawned_browser != -1:
            logger.debug("Spawned browser: " + spawned_browser.name)
            browsers.append(spawned_browser)

    barr = BrowserArray(*browsers)
    return barr
