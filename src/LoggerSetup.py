import os, logging


def set_up_logging(logfile='obsidian.log'):
    """
    1. DEBUG (and higher) logs to file
    2. INFO (and higher) logs to console
    3. Can have named loggers (their name appears next to the message)

    Define custom logger:
        mylog = logging.getLogger('obs.navigation')  # => logger called 'obs.navigation'
    Log to root logger:
        logging.info('my not very important log')

    Levels:
        - Debug
        - Info
        - Error
        - Critical
    """
    try:
        os.remove(logfile)
    except OSError:
        open(logfile, 'w+')

    # Only let Selenium log Warnings and up
    logging.getLogger("selenium.webdriver.remote.remote_connection").setLevel(logging.WARNING)

    # Set up logging to file
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s | %(name)-15s | [%(levelname)-8s] | %(message)s',
                        datefmt='%d-%m %H:%M',
                        filename=logfile,
                        filemode='w')
    # Define a Handler which writes INFO messages or higher to the sys.stderr
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    # Set a format which is simpler for console use
    formatter = logging.Formatter('[%(levelname)-8s] %(name)-15s: %(message)s')
    # Tell the handler to use this format
    console.setFormatter(formatter)
    # Add the handler to the root logger
    logging.getLogger('').addHandler(console)
