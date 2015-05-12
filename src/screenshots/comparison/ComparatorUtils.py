__author__ = 'nico'

import logging
from SimpleCV import Image as SCVImage

logger = logging.getLogger("ComparatorUtils")

def match_sizes(img_a, img_b, scale='up', destructive=False):
    """
    Get the filename of two images, and match their sizes.
    :parameter scale: Scale 'up' or 'down'. Increase size of the smallest one, or viceversa.
    :type scale: str
    :parameter destructive: Overwrite the scaled up/down image
    :type destructive: bool
    """
    scale = 'up' if scale not in ('up', 'down') else scale
    i1, i2 = build_images(img_a, img_b)
    if i1.size() == i2.size():
        logger.info("Not changing sizes")
        return i1, i2
    i1pixels = reduce(lambda x, y: x * y, i1.size())  # why?
    i2pixels = reduce(lambda x, y: x * y, i2.size())  # because I can
    biggest = i1 if i1pixels > i2pixels else i2
    smallest = i1 if i1pixels < i2pixels else i2
    if scale == 'up':
        target = biggest
        victim = smallest
        logger.info("Scaling %s to match %s" % (victim.filename, biggest.filename))
    else:
        target = smallest
        victim = biggest
        logger.info("Scaling %s to match %s" % (victim.filename, smallest.filename))
    saved_filename = victim.filename
    victim = victim.scale(target.size()[0], target.size()[1])
    if destructive:
        logger.debug("Overwriting: %s" % saved_filename)
        try:
            victim.save(saved_filename)
        except IOError:
            logger.error("Could not save file: %s. Check if you have appropiate permissions." % saved_filename)
    return target, victim


def build_images(img_a, img_b):
    try:
        if not isinstance(img_a, SCVImage):
            img_a = SCVImage(str(img_a))
        if not isinstance(img_b, SCVImage):
            img_b = SCVImage(str(img_b))
    except IOError:
        logger.critical("Could not open file. Check that both %s and %s exist." % (img_a, img_b))
        raise
    return img_a, img_b


def resolve_variable_names(filename, images=None, action=None):
    """
    Replaces variable names for their real values in the filename that will be saved
    :param filename: Filename of the file that will be saved
    :type filename str
    :param images: Filenames of images that are compared
    :type images tuple
    :param action: Action/Comparing method used
    :type action str
    :return: 'filename' with variables changed
    """
    from src.CustomUtils import get_random_str, get_current_time
    filename = filename.replace("$random", get_random_str(8))
    filename = filename.replace("$date", get_current_time())
    if images is not None:
        try:
            assert isinstance(images, tuple)
            filename = filename.replace("$images", "%s-%s" % (images[0], images[1]))
        except AssertionError:
            logger.warning("'images' must be a tuple. Setting as random string instead.")
            filename = filename.replace("$images", get_random_str(8))
    if action is not None:
        filename = filename.replace("$action", action)
    return filename
