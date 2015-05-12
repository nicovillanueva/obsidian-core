__author__ = 'nico'

from PIL import Image

class ImageStitcher():

    def __init__(self, wid=0, hei=0):
        self.images = []
        self.width = wid
        self.height = hei

    def add_image(self, img, x=0, y=0):
        """
        Adds an image to the final, all patched up, image
        :param img: Image to add to the bigger picture
        :param x: X position of the new image
        :param y: Y position of the new image
        """
        new_wid = img.size[0] + x
        new_hei = img.size[1] + y
        if new_wid > self.width: self.width = new_wid
        if new_hei > self.height: self.height = new_hei
        self.images.append( {"img": img, "x": x, "y": y} )


    def build_final(self):
        "Returns a big image containing all of the previously added images"
        final_img = Image.new("RGB", (self.width, self.height), "black")
        for each in self.images:
            final_img.paste(each["img"], (each["x"], each["y"]))
        return final_img
