# coding=utf8

"""

 MP3 Voice Stamp

 Athletes' companion: adds synthetized voice overlay with various
 info and on-going timer to your audio files

 Copyright ©2018 Marcin Orlowski <mail [@] MarcinOrlowski.com>

 https://github.com/MarcinOrlowski/Mp3VoiceStamp

"""

from __future__ import print_function

import sys

from mp3voicestamp_app.util import Util
from mp3voicestamp_app.log import Log


class Tools(object):
    KEY_FFMPEG = 'ffmpeg'
    KEY_NORMALIZE = 'normalize'
    KEY_SOX = 'sox'
    KEY_ESPEAK = 'espeak'

    __tools_map = {}

    def __init__(self):
        self.__tools_map = {}
        self.__check_env_called = False

    def ensure_check_env_called(self):
        if not self.__check_env_called:
            raise RuntimeError('check_env() must be called prior using other methods!')

    def check_env(self):
        """Checks if all external tools we need are already available and in $PATH
        """
        if sys.platform == 'win32':
            self.__tools_map = {
                self.KEY_FFMPEG: 'ffmpeg.exe',
                self.KEY_SOX: 'sox.exe',
                self.KEY_ESPEAK: 'espeak.exe',
            }
        else:
            self.__tools_map = {
                self.KEY_FFMPEG: 'ffmpeg',
                self.KEY_SOX: 'sox',
                self.KEY_ESPEAK: 'espeak',
            }

        for _, tool in self.__tools_map.items():
            failed = False
            if Util.which(tool) is None:
                Log.e("'{}' not found.".format(tool))

            if failed:
                Util.abort('Required tools not found. See documentation for installation guidelines.')

        # sometimes normalize is called normalize-audio (i.e. in Debian/Ubuntu)
        # so we do special checks just for this one particular tool
        normalize_check_result = False
        if sys.platform == 'win32':
            normalize = 'normalize.exe'
            if Util.which(normalize) is not None:
                self.__tools_map[self.KEY_NORMALIZE] = normalize
                normalize_check_result = True
        else:
            normalize = 'normalize'
            if Util.which(normalize) is not None:
                self.__tools_map[self.KEY_NORMALIZE] = normalize
                normalize_check_result = True
            else:
                normalize = 'normalize-audio'
                if Util.which(normalize) is not None:
                    self.__tools_map[self.KEY_NORMALIZE] = normalize
                    normalize_check_result = True

        if not normalize_check_result:
            Util.abort('2: "{}" not found. See documentation for installation guidelines.'.format('normalize'))

        self.__check_env_called = True

    def get_tool(self, key):
        self.ensure_check_env_called()
        return self.__tools_map.get(key)
