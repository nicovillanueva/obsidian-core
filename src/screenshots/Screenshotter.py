import logging, time, datetime, os, glob
from Screenshot import Screenshot
from PIL import Image

import ScreenshotterUtils as Utils


class Screenshotter:

    def __init__(self):
        self.logger = logging.getLogger('Screenshotter')

    # --------------------

    @staticmethod
    def save_screenshot(drv, path="", filename=""):
        """
        Get a browser to take a screenshot with, and a path to save the screenshot to.
        The filename will be decided using the browser's name.
        Returns the screenshot entity.
        """
        scr = Screenshotter()
        logger = scr.logger

        wid, hei = drv.get_window_size().values()
        logger.debug("Window size: " + str(wid) + "x" + str(hei))

        if "firefox" in drv.name:
            sshot_path = scr.save_screenshot_firefox(drv, path, filename)
            
        elif "internet explorer" in drv.name:
            sshot_path = scr.save_screenshot_ie(drv, path, filename)
            
        elif "chrome" in drv.name:
            sshot_path = scr.save_screenshot_chrome(drv, path, filename)

        elif "phantomjs" in drv.name:
            sshot_path = scr.save_screenshot_phantomjs(drv, path, filename)
        else:
            logger.error("Non recognized browser!\nOnly Firefox, Chrome and IE are supported (for now, anyways.)")
            raise ValueError("Non recognized browser!")

        s = Screenshot(sshot_path, drv.current_url,
                       datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                       drv.name, wid, hei)
        s.images = scr.find_all_images(drv)

        if "$hash" in s.path:
            # Hash value must be replaced after writing the file
            hashed_path = s.path.replace("$hash", s.hashvalue)
            os.renames(s.path, hashed_path)
            s.path = hashed_path

        logger.debug("Taken screenshot with path: " + s.path)

        return s

    # ====================

    def save_screenshot_firefox(self, drv, path="", filename=""):
        wid, hei = drv.get_window_size().values()
        imgpath = Utils.resolve_path(path, filename, drv)
        drv.save_screenshot(imgpath)
        scrnshot = Image.open(imgpath)
        self.crop_image_firefox(scrnshot, wid, hei)
        return imgpath

    def crop_image_firefox(self, scrn, window_width, window_height):
        """
        When resizing a window, Firefox tends to keep the window size previous to
        the resize. Therefore, taking a screenshot results in an image with lots of whitespace.
        This method crops it to a desired size.
        """
        i_wid, i_hei = scrn.size
        window_width = (window_width if window_width < i_wid else i_wid)  # Sometimes the image gets expanded
        scrn.crop((0, 0, window_width, i_hei)).save(scrn.filename)
        self.logger.debug("Image size: " + str(i_wid) + "x" + str(i_hei))
        self.logger.debug("Screensize: " + str(window_width) + "x" + str(window_height))
        self.logger.debug("Cropped to: " + str(window_width) + "x" + str(i_hei))

    def save_screenshot_ie(self, drv, path="", filename=""):
        imgpath = Utils.resolve_path(path, filename, drv)
        drv.save_screenshot(imgpath)
        return imgpath

    def save_screenshot_phantomjs(self, drv, path="", filename=""):
        imgpath = Utils.resolve_path(path, filename, drv)
        drv.save_screenshot(imgpath)
        return imgpath

    def save_screenshot_chrome(self, drv, path="", filename=""):
        from StringIO import StringIO
        from base64 import decodestring
        from ImageStitcher import ImageStitcher

        drv.execute_script("window.document.body.scrollTop = 0")
        time.sleep(0.5)  # Avoiding overlaps, the cheap way
        
        do_scroll = lambda y: drv.execute_script("window.document.body.scrollTop += " + str(y))
        scroll_top = lambda: drv.execute_script("return window.document.body.scrollTop")
        page_height = drv.execute_script("return window.document.body.scrollHeight")
        view_height = drv.execute_script("return window.innerHeight")

        iterations = float(page_height) / float(view_height)
        imgstitcher = ImageStitcher()
        while iterations > 0.0:
            if iterations < 1.0:
                last = Image.open(StringIO(decodestring(drv.get_screenshot_as_base64())))
                last_width, last_height = last.size
                cropped_height = (last_height * iterations) / 100
                imgstitcher.add_image(last.crop((0, int(cropped_height), last_width, last_height)), 0, scroll_top())
                break
            
            tmp = Image.open(StringIO(decodestring(drv.get_screenshot_as_base64())))  # Take screenshot in memory
            imgstitcher.add_image(tmp, 0, scroll_top())

            do_scroll(view_height)
            time.sleep(0.5)  # Overlaps 1st and 2nd images otherwise.
            iterations -= 1.0

        imgpath = Utils.resolve_path(path, filename, drv)
        imgstitcher.build_final().save(imgpath)
        return imgpath

    def find_all_images(self, drv):
        """
        Gets all of the images' sizes from the page.
        The sizes are saved to a dict, and all sizes are grouped up in a list which is returned
        :param drv: Driver to get images from
        :rtype : list
        """
        img_getter = """
            var sizes = []
            for(var i = 0; i < document.images.length; i++){
                var t = document.images[i].clientTop
                var l = document.images[i].clientLeft
                var w = document.images[i].clientWidth
                var h = document.images[i].clientHeight
                sizes.push({top: t,
                            left: l,
                            width: w,
                            height: h
                            })
            }
            return sizes
        """
        return drv.execute_script(img_getter)
