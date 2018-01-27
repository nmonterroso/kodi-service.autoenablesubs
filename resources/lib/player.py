# -*- coding: utf-8 -*-

from resources.lib import kodiutils
import xbmc


class AutoSubEnablePlayer(xbmc.Player):
    def __init__(self, *args, **kwargs):
        xbmc.Player.__init__(self)
        self.logger = kwargs['logger']

    def get_preferred_lang(self):
        return 'eng'

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
                    'subtitleenabled'
                ]
            }
        })

        return (
            details['currentaudiostream']['language'],
            details['subtitleenabled']
        )

    def needs_subs(self, current_lang, preferred_lang):
        return current_lang != preferred_lang

    def get_preferred_lang_sub_index(self, preferred_lang):
        for index, lang in enumerate(self.getAvailableSubtitleStreams()):
            self.logger.debug("preferred_lang %s sub lang %s", preferred_lang, lang)
            if lang == preferred_lang:
                return index

        return None

    def onPlayBackStarted(self):
        if self.isPlayingVideo():
            active_player_id = self.get_active_player_id()
            preferred_lang = self.get_preferred_lang()
            (current_audio_lang, is_sub_enabled) = self.get_stream_details(active_player_id)

            # subtitles already on, or language is already the user desired language
            if is_sub_enabled or not self.needs_subs(current_audio_lang, preferred_lang):
                self.logger.debug("subs not needed")
                return

            sub_index = self.get_preferred_lang_sub_index(preferred_lang)
            if sub_index is None:
                self.logger.debug("desired sub index not found :(")
                return

            self.logger.debug("desired sub index %s", sub_index)
            self.setSubtitleStream(sub_index)
            self.showSubtitles(True)

            # seek to beginning, since there is often a delay in subs turning on (keyframes?)
            # TODO: how does this work when resuming a video?
            self.seekTime(0)
