from Capture import Capture


class Screenshot(Capture):
    
    def __init__(self, imgpath, url, date_taken=None, browser=None, wid=-1, hei=-1):
        super(Screenshot, self).__init__(imgpath)

        self.images = 0
        self.url = url
        self.browser = browser
        self.date_taken = date_taken
        self.width = wid
        self.height = hei
