import os

import cv2
import numpy
import stbt


def find_selection_horizontal_repeat(
        frame, background, region=stbt.Region.ALL, match_threshold=0.95):

    """Find the selected menu item by looking for the specified background.

    This is an example to demonstrate that you can implement your own custom
    image processing with OpenCV.

    :param frame: An OpenCV image, as returned by `stbt.get_frame` or
        `cv2.imread`. If `None`, will pull a new frame from the system under
        test.

    :param background: The path to a 1-pixel-wide image of your
        system-under-test's menu selection/highlight.

    :param region: If specified, restrict the search to this region of the
        frame.

    :returns: A `Selection` object representing the selected item.

    Example::

        >>> frame = load_image("../selftest/screenshots/roku-home.png")
        >>> find_selection_horizontal_repeat(
        ...     frame, "images/roku-menu-selection-background.png")
        Selection(region=Region(x=116, y=157, right=483, bottom=208),
                  text=u'Home')

    """

    if frame is None:
        frame = stbt.get_frame()
    frame = crop(frame, region)

    bg = load_image(background)

    correlation = 1 - cv2.matchTemplate(frame, bg, cv2.TM_SQDIFF_NORMED)
    _, max_, _, _ = cv2.minMaxLoc(correlation)
    selection_region = None
    if max_ >= match_threshold:
        # Find y coordinate
        rowmax = numpy.amax(correlation, axis=1)
        goodness = rowmax
        _, _, _, maxloc = cv2.minMaxLoc(goodness)
        y = maxloc[1]

        # Got the y position, now work out the horizontal extents
        line_uint8 = numpy.uint8(correlation[y, :]*255)
        _, binary = cv2.threshold(line_uint8, 0, 255,
                                  cv2.THRESH_OTSU | cv2.THRESH_BINARY)
        binary = binary.flatten()

        nonzeros = list(_combine_neighbouring_extents(
            list(_zeros_to_extents(binary.nonzero()[0]))))
        if nonzeros:
            widest = max(nonzeros, key=lambda a: a[1] - a[0])
            x, right = widest
            selection_region = (
                stbt.Region(x, y, right=right, bottom=y + bg.shape[0])
                .translate(x=max(0, region.x), y=max(0, region.y)))
            if selection_region.width > 10:
                # Remove the rounded corners of the selection; after subtracting
                # the background they look like single-quotes to the OCR engine.
                selection_region = selection_region.extend(x=5, right=-5)

    if not selection_region:
        stbt.debug(
            "find_selection didn't find match (%.2f) above the threshold (%.2f)"
            % (max_, match_threshold))

    return Selection(selection_region, frame, bg)


class Selection(object):
    def __init__(self, region, frame, background):
        self.region = region
        self._frame = frame
        self._background = background
        self._text = None

    def __nonzero__(self):
        return self.region is not None

    def __eq__(self, other):
        return (isinstance(other, Selection) and
                self.region == other.region and
                self.text == other.text)

    def __ne__(self, other):
        return not self.__eq__(other)

    def __str__(self):
        return "Selection(region=%r, text=%r)" % (self.region, self.text)

    def __repr__(self):
        return self.__str__()

    @property
    def text(self):
        if self._text is None and self.__nonzero__():
            diff = cv2.cvtColor(
                cv2.absdiff(
                    crop(self._frame, self.region),
                    numpy.repeat(self._background, self.region.width, 1)),
                cv2.COLOR_BGR2GRAY)
            self._text = stbt.ocr(diff)
        stbt.debug("Selection text: %s" % self._text)
        return self._text


def crop(frame, region):
    frame_region = stbt.Region(
        x=0, y=0, width=frame.shape[1], height=frame.shape[0])
    region = stbt.Region.intersect(frame_region, region)
    return frame[region.y:region.bottom, region.x:region.right]


def load_image(relative_path):
    return cv2.imread(os.path.join(os.path.dirname(__file__), relative_path))


def _zeros_to_extents(zeros):
    """
    >>> list(_zeros_to_extents([3,4,5,7,8,9,10,15,21,22]))
    [(3, 6), (7, 11), (15, 16), (21, 23)]
    >>> list(_zeros_to_extents([]))
    []
    >>> list(_zeros_to_extents([3]))
    [(3, 4)]
    """
    if len(zeros) == 0:
        return
    bottom = zeros[0]
    last = zeros[0]
    for x in zeros[1:]:
        if x == last + 1:
            last = x
            continue
        else:
            yield (bottom, last + 1)
            bottom = x
            last = x
    yield (bottom, last + 1)


def _combine_neighbouring_extents(extents, distance_px=10):
    """
    >>> list(_combine_neighbouring_extents(
    ...     [(1, 6), (7, 11), (12, 16), (18, 23)],
    ...     distance_px=1))
    [(1, 16), (18, 23)]
    """
    left, right = extents[0]
    for x in extents[1:]:
        if x[0] <= (right + distance_px):
            right = x[1]
        else:
            yield (left, right)
            left, right = x
    yield (left, right)
