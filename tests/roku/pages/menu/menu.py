import stbt


class Menu(stbt.FrameObject):
    """Represents the menu on the Roku home screen (Home, Settings, etc).

    This is a fixed-focus menu: the position of the selection stays the same,
    but the menu entries scroll up & down, into & out of the selection.

    For details about FrameObjects see
    <https://stb-tester.com/manual/object-repository>
    """

    @property
    def is_visible(self):
        return stbt.match("menu-selection-background.png",
                          frame=self._frame, region=self.selection_region)

    @property
    def selection(self):
        return stbt.ocr(
            frame=self._frame,
            mode=stbt.OcrMode.SINGLE_LINE,
            region=self.selection_region)

    @property
    def selection_region(self):
        return stbt.Region(x=113, y=160, width=371, height=45)  # Fixed focus

    @staticmethod
    def to_home():
        for _ in range(5):
            stbt.press("KEY_HOME")
            menu = stbt.wait_until(
                Menu, predicate=lambda m: m.selection == "Home")
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
