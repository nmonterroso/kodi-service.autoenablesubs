# -*- coding: utf-8 -*-

from resources.lib import kodiutils
import xbmc


class AutoSubEnablePlayer(xbmc.Player):
    def __init__(self, *args, **kwargs):
        xbmc.Player.__init__(self)
        self.logger = kwargs['logger']

    def get_active_player_id(self):
        active_player = kodiutils.jsonrpc(1, {
            'method': 'Player.GetActivePlayers'
        })

        return active_player[0]['playerid']

    def get_stream_details(self, player_id):
        details = kodiutils.jsonrpc("VideoGetProperties", {
            'method': 'Player.GetProperties',
            'params': {
                'playerid': player_id,
                'properties': [
                    'currentaudiostream',
                    'subtitleenabled',
                    'currentsubtitle',
                    # 'subtitles'
                ]
            }
        })

        return (
            details['currentaudiostream']['language'],
            details['subtitleenabled'],
            details['currentsubtitle']['index']
        )

    def needs_subs(self, current_language):
        # TODO: get from a setting
        return not current_language == 'eng'

    def get_desired_sub_index(self):
        return 0
        # return next((x for x in self.getAvailableSubtitleStreams() if x == 'eng'), None)

    def onPlayBackStarted(self):
        if self.isPlayingVideo():
            active_player_id = self.get_active_player_id()
            (current_audio_lang, is_sub_enabled, current_sub_index) = self.get_stream_details(active_player_id)

            # subtitles already on, or language is already the user desired language
            if is_sub_enabled or not self.needs_subs(current_audio_lang):
                self.logger.debug("subs not needed")
                return

            desired_sub_index = self.get_desired_sub_index()
            if desired_sub_index is None:
                self.logger.debug("desired sub index not found :(")
                return

            self.logger.debug("desired sub index %s", desired_sub_index)
            self.setSubtitleStream(desired_sub_index)
            self.showSubtitles(True)

            # seek to beginning, since there is often a delay in subs turning on (keyframes?)
            # TODO: how does this work when resuming a video?
            self.seekTime(0)
