import logging

class BrowserArray:

    def __init__(self, *browsertuple):
        self.browsers = browsertuple
        self.logger = logging.getLogger('obs.BrowserArray')

    def get(self, url, cookie=None):
        """
        Propagate the get() method.
        Adds stage cookie if needed.
        """
        for br in self.browsers:
            br.get(url)

        baseurl = self._get_base_url(url)
        for br in self.browsers:
            for each in cookie:
                if not self._check_for_cookie(each.get("name")):
                    br.get(baseurl)
                    self._add_cookie(each)
                    br.get(url)
                else:
                    self.logger.debug("Not adding cookie: %s" % (each.get("name")))

                self.logger.debug("Current cookies of %s:" % br.name)
                self.logger.debug(br.execute_script("return document.cookie"))

    def set_window_size(self, window_width, window_height):
        for br in self.browsers:
            br.set_window_position(0,0)
            br.set_window_size(window_width, window_height)

    def maximize_window(self):
        for br in self.browsers:
            br.set_window_position(0,0)
            br.maximize_window()
    
    def save_screenshot(self, target_dir=None, target_file=None):
        """
        Propagates the save_screenshot() method to each browser.
        Can specify to which folder to save the screenshots.
        Return an array of screenshot entities
        """
        from ..screenshots.Screenshotter import Screenshotter
        sshots = []
        for br in self.browsers:
            sshots.append(Screenshotter.save_screenshot(br, target_dir, target_file))
        return sshots

    def get_browser(self, browsername):
        """
        Get a given browser from the browser array
        """
        for br in self.browsers:
            if(browsername in str(type(br))):
                return br

    def quit(self):
        """
        Propagate the quit() method
        Meaning, close all browsers
        """
        for br in self.browsers:
            br.quit()

    def _get_base_url(self, url):
        from urlparse import urlparse
        parsedurl = urlparse(url)
        return parsedurl.scheme + "://" + parsedurl.hostname 

    def _check_for_cookie(self, name):
        for each in self.browsers:
            cookies = each.execute_script("return document.cookie")
            if name not in cookies:
                self.logger.debug("Cookie %s not in browser" % (name))
                return False
        return True

    def _add_cookie(self, cookie):
        append_to_cookie = lambda c,k,v: c[:-1] + ";" + k + "=" + v + "\""
        
        name = cookie.get("name")
        value = cookie.get("value")
        path = cookie.get("path")
        expiry = cookie.get("expiry")
        domain = cookie.get("domain")
        secure = cookie.get("secure")

        script_cookie = "document.cookie=\"%s=%s\"" % (name, value)
        
        if path not in (None, ""): script_cookie = append_to_cookie(script_cookie, "path", path)
        if expiry not in (None, ""): script_cookie = append_to_cookie(script_cookie, "expiry", expiry)
        if domain not in (None, ""): script_cookie = append_to_cookie(script_cookie, "domain", domain)
        if secure not in (None, ""): script_cookie = append_to_cookie(script_cookie, "secure", secure)
        
        self.logger.info("Adding cookie: " + script_cookie)
        for each in self.browsers:
            each.execute_script(script_cookie)