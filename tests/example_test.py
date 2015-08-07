from time import sleep

import stbt


def test_that_live_tv_is_playing():
    stbt.press('KEY_CLOSE')  # Close any open menus
    assert stbt.wait_for_motion()


def test_that_stb_tester_logo_is_shown():
    stbt.press('KEY_CHANNELUP')
    assert stbt.wait_for_match('stb-tester-logo.png')


def test_read_menu():
    stbt.press('KEY_CLOSE')
    sleep(1)
    stbt.press('KEY_MENU')
    sleep(1)
    print stbt.ocr()
