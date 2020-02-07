# coding:utf-8

from .pages.menu import Menu
from .pages.networkabout import NetworkAbout


def test_settings_network_about():
    Menu.to_home().select("Settings", "Network", "About")
    assert NetworkAbout().status == "Connected"
