from stbt import match, press, wait_until


def test_that_roku_home_shows_netflix_player():
    to_roku_home()
    assert wait_until(lambda: match("images/netflix-tile.png"))


def test_entering_the_settings_menu():
    to_roku_home()

    for _ in range(5):
        press("KEY_DOWN")
        if wait_until(lambda: find_selection().text == "Settings",
                      timeout_secs=2):
            break
    else:
        assert False, "Failed to find 'Settings' menu item"

    press("KEY_OK")
    assert wait_until(lambda: find_selection().text == "Network"), \
        "Failed to find 'Network' settings sub-menu"

    press("KEY_BACK")
    assert wait_until(lambda: find_selection().text == "Settings"), \
        "Pressing BACK didn't take me back to 'Settings' menu item"


def test_that_screensaver_appears_if_i_do_nothing():
    to_roku_home()
    assert wait_until(lambda: match("images/roku-screensaver.png"),
                      timeout_secs=2 * 60)


def to_roku_home():
    for _ in range(5):
        press("KEY_HOME")
        if wait_until(lambda: find_selection().text == "Home"):
            break
    else:
        assert False, "Failed to find Roku Home after pressing HOME 5 times"


def find_selection(frame=None):
    import utils

    return utils.find_selection_horizontal_repeat(
        frame, "images/roku-menu-selection-background.png")
