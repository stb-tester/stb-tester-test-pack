import stbt
from time import sleep

def test_that_stb_tester_logo_is_shown():
    stbt.press('KEY_CHANNELUP')
    sleep(1)
    assert stbt.match('stb-tester-logo.png')
