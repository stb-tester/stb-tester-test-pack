import stbt
from time import sleep

stbt.press('KEY_CHANNELUP')
assert stbt.match('stb-tester-logo.png')
