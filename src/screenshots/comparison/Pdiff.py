from ..Capture import Capture


class Pdiff(Capture):
    """
    A Diff image that represents the absolute
    difference between two other images.
    """

    between = []

    def __init__(self, between, imgpath):
        super(Pdiff, self).__init__(imgpath)
        self.between = between
