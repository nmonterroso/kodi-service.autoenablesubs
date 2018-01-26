# -*- coding: utf-8 -*-

import logging
import xbmc
import xbmcaddon

from resources.lib import player

ADDON = xbmcaddon.Addon()
logger = logging.getLogger(ADDON.getAddonInfo('id'))


def run():
    monitor = xbmc.Monitor()
    player_monitor = player.AutoSubEnablePlayer(logger=logger)

    while not monitor.abortRequested():
        if monitor.waitForAbort(10):
            break

    del player_monitor
