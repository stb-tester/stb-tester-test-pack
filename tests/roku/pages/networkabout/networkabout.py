import stbt


class NetworkAbout(stbt.FrameObject):
    """The 'Settings > Network > About' screen.

    For details about FrameObjects see
    <https://stb-tester.com/manual/object-repository>
    """

    @property
    def is_visible(self):
        from ..menu import Menu
        return Menu(frame=self._frame).selection == "About"

    @property
    def status(self):
        return self._read_text("Status")

    @property
    def connection_type(self):
        return self._read_text("Connection type")

    @property
    def ip_address(self):
        return self._read_text("IP address", IP_ADDRESS_PATTERN)

    @property
    def gateway(self):
        return self._read_text("Gateway", IP_ADDRESS_PATTERN)

    def _read_text(self, title, patterns=None):
        title = stbt.match_text(
            title, frame=self._frame,
            region=stbt.Region(x=620, y=145, right=950, bottom=460),
            text_color=(124, 94, 114))
        if not title:
            stbt.debug("NetworkAbout: Didn't find %r" % title)
            return None
        region = title.region.right_of().extend(x=10, y=-5, bottom=10)
        return stbt.ocr(self._frame, region, tesseract_user_patterns=patterns)


_octet = [r"\d", r"\d\d", r"\d\d\d"]
IP_ADDRESS_PATTERN = [a + "." + b + "." + c + "." + d
                      for a in _octet
                      for b in _octet
                      for c in _octet
                      for d in _octet]
