# coding:utf-8

import stbt
from stbt import wait_until


def test_settings_network_about():
    Menu.to_home().select("Settings", "Network", "About")
    assert NetworkAbout().status == "Connected"


class Menu(stbt.FrameObject):
    """Represents the menu on the Roku home screen (Home, Settings, etc).

    This is a fixed-focus menu: the position of the selection stays the same,
    but the menu entries scroll up & down, into & out of the selection.

    For details about FrameObjects see
    <https://stb-tester.com/manual/object-repository>
    """

    @property
    def is_visible(self):
        ignore_text = stbt.MatchParameters(confirm_method="none")
        return stbt.match("images/roku/menu-selection-background.png",
                          frame=self._frame, region=self.selection_region,
                          match_parameters=ignore_text)

    @property
    def selection(self):
        return stbt.ocr(
            frame=self._frame,
            mode=stbt.OcrMode.SINGLE_LINE,
            # Exclude the edges & corners of the button:
            region=self.selection_region.extend(x=5, y=2, right=-5, bottom=-2))

    @property
    def selection_region(self):
        return stbt.Region(x=111, y=158, right=488, bottom=207)  # Fixed focus

    @staticmethod
    def to_home():
        for _ in range(5):
            stbt.press("KEY_HOME")
            menu = wait_until(Menu, predicate=lambda m: m.selection == "Home")
            if menu:
                return menu
        assert False, "Failed to find Roku Home after pressing KEY_HOME 5 times"

    def select(self, menu, *submenus):
        """Select the specified menu item (and sub-menus, if specified).

        Example::

            Menu().select("Settings", "Network", "About")

        """
        assert self.is_visible
        original_value = self.selection
        f = self  # FrameObject of current video-frame being processed
        target = menu
        for _ in range(20):
            assert f.is_visible
            current_value = f.selection
            if current_value == target:
                stbt.debug("Menu.select: Found %s" % target)
                if submenus:
                    transition = stbt.press_and_wait("KEY_OK")
                    assert transition
                    f = Menu(frame=transition.frame)
                    assert f.selection != current_value
                    return f.select(submenus[0], *submenus[1:])
                else:
                    return f
            stbt.debug("Menu.select: target=%r, current=%r, "
                       "going to press KEY_DOWN"
                       % (target, current_value))
            transition = stbt.press_and_wait("KEY_DOWN")
            assert transition
            f = Menu(frame=transition.frame)
            assert f.is_visible
            assert f.selection != current_value
            assert f.selection != original_value, (
                "Menu.select wrapped around to %r without finding %r"
                % (original_value, target))


class NetworkAbout(stbt.FrameObject):
    """The 'Settings > Network > About' screen.

    For details about FrameObjects see
    <https://stb-tester.com/manual/object-repository>
    """

    @property
    def is_visible(self):
        menu = Menu(frame=self._frame)
        return menu.selection == "About"

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
