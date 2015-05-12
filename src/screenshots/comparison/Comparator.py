import os
import logging
import numpy
import inspect
from SimpleCV import Image as SCVImage
from SimpleCV import Color
import ComparatorUtils as Utils

logger = logging.getLogger('obs.Comparator')

"""
To add more comparing methods:
    - Parameters: First two parameters must be images to compare (filepaths or SimpleCV Images)
                  The extra parameters are encouraged to have default values, although they are not required
    - Returns:
        It must always return a dict:
        On success:
            { "result": <JSON serializable result (text, integer or boolean)> }
        On failure:
            { "result": "error", "reason": <reason of failure> }  # it may have more keys, such as "data", for example
"""


def pixels_difference(img_a, img_b):
    """
    Gets two image filepaths, and returns the
    amount of different pixels
    between them.
    """
    try:
        i1, i2 = Utils.build_images(img_a, img_b)
    except IOError:
        return -1
    i1, i2 = Utils.match_sizes(i1, i2)
    difference = (i1 - i2) + (i2 - i1)
    matrix = difference.getNumpy()
    flat = matrix.flatten()
    nonzero = numpy.count_nonzero(flat)
    logger.info('There are %i different pixels between %s and %s' % (nonzero, img_a, img_b))
    return {"result": nonzero}


def difference_percentage(img_a, img_b):
    """
    Gets two image filepaths, and returns the
    absolute difference percentage
    between them.
    """
    try:
        i1, i2 = Utils.build_images(img_a, img_b)
    except IOError:
        return -1
    i1, i2 = Utils.match_sizes(i1, i2)
    difference = (i1 - i2) + (i2 - i1)
    matrix = difference.getNumpy()
    flat = matrix.flatten()
    non_zero = numpy.count_nonzero(flat)
    perc_change = 100 * float(non_zero) / float(len(flat))
    logger.info('Difference between %s and %s: %f' % (img_a, img_b, perc_change))
    return {"result": perc_change}


def size_difference(img_a, img_b):
    """
    Get two image filepaths, and return the file size difference
    between them both (in bytes).
    """
    try:
        size_a = os.path.getsize(img_a)
        size_b = os.path.getsize(img_b)
    except OSError:
        logger.error("Could not open file. Check that both %s and %s exist." % (img_a, img_b))
        return -1
    difference = abs(size_a - size_b)
    logger.info("%i bytes between %s and %s" % (difference, img_a, img_b))
    return {"result": difference}


def generate_pdiff(img_a, img_b, grayscale=False, save_as=None):
    """
    Get two image filepaths. If the third parameter is None,
    only the SCVImage instance of the pdiff is returned. If it's a file path, the pdiff is also saved.
    Create a pdiff image between the two images.
    """
    if inspect.stack()[1][3] == "_main" and save_as is None:
        # Cannot run as a test, if you do not provide a filename to save the pdiff as.
        err = "'save_as' is required when running a 'generate_pdiff' test"
        logger.error(err)
        return {'result': "error", 'reason': err}
    i1, i2 = Utils.build_images(img_a, img_b)
    i1, i2 = Utils.match_sizes(i1, i2)
    if grayscale:
        i1 = i1.toGray()
        i2 = i2.toGray()
    img_diff = (i1 - i2) + (i2 - i1)
    img_diff = img_diff.getPIL().convert(mode='RGB')
    if isinstance(save_as, (str, unicode)):
        try:
            save_as = Utils.resolve_variable_names(save_as, (img_a, img_b), "generate_pdiff")
            img_diff.save(save_as)
        except IOError:
            err = "Could not save file: %s. Check if you have appropiate permissions." % save_as
            logger.error()
            return {"result": "error", "reason": err}
        except KeyError:
            err = "Could not save file: %s. Make sure that the extension is .png" % save_as
            logger.error(err)
            return {"result": "error", "reason": err}
    return SCVImage(img_diff) if save_as is None else {"result": save_as}


def highlight_differences(img_a, img_b, grayscale=False, save_as=None, amount=3):
    """Create a pdiff image, and highlight the biggest pdifference areas.

    :parameter amount: Amount of difference areas to highlight
    :type amount: int
    :parameter grayscale If True, converts and compares the images in grayscale mode
    :type grayscale bool
    :parameter save_as If not None, saves the pdiff with highlighted differences
    :type save_as str
    """
    i1, i2 = Utils.build_images(img_a, img_b)
    d = generate_pdiff(i1, i2, grayscale=grayscale, save_as=None)
    b = d.findBlobs()
    if b is None:
        logger.info("No differences found")
        return i1
    b = b[-amount:]
    b.reverse()
    map(lambda x: x.drawRect(color=Color.RED, width=-1, alpha=128), b)
    if isinstance(save_as, (unicode, str)):
        try:
            save_as = Utils.resolve_variable_names(save_as, (img_a, img_b), "highlight_differences")
            d.save(save_as)
        except IOError:
            err = "Could not save file: %s. Check if you have appropiate permissions." % save_as
            logger.error(err)
            return {"result": "error", "reason": err}
        except KeyError:
            err = "Could not save file: %s. Make sure that the extension is .png" % save_as
            logger.error(err)
            return {"result": "error", "reason": err}
    return SCVImage(d) if save_as is None else {"result": save_as}
