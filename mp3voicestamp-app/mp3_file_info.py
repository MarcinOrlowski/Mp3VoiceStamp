# coding=utf8

"""

 MP3 Voice Stamp

 Athletes' companion: add synthetized voice overlay with various
 info and on-going timer to your audio files

 Copyright ©2018 Marcin Orlowski <mail [@] MarcinOrlowski.com>

 https://github.com/MarcinOrlowski/mp3voicestamp

"""

from __future__ import print_function

import os
from mutagen.mp3 import MP3
from util import Util


class Mp3FileInfo(object):

    def __init__(self, file_name):
        if not os.path.isfile(file_name):
            raise OSError('File not found: "{}"'.format(file_name))

        self.file_name = file_name

        self.mp3 = MP3(file_name)
        self.duration = int(round(self.mp3.info.length / 60 + 0.5))
        self.bitrate = self.mp3.info.bitrate

        # get track title either from tag, or from filename
        self.title = self.__get_tag('TIT2', str(file_name[:-4].replace('_', ' ')))
        self.artist = self.__get_tag('TPE1')
        self.album_artist = self.__get_tag('TPE2')
        self.album_title = self.__get_tag('TALB')
        self.composer = self.__get_tag('TCOM')
        self.performer = self.__get_tag('TOPE')
        self.comment = self.__get_tag('COMM::XXX:')

    def __get_tag(self, tag, default=''):
        return default if tag not in self.mp3 else str(self.mp3[tag])

    def format_title(self, title_fmt, extra_placeholders=None):
        """ Formats track title string (used for voice synthesis) using MP3 tags represented by placeholders.
        """

        if extra_placeholders is None:
            extra_placeholders = {}

        if not isinstance(extra_placeholders, dict):
            raise ValueError('Placeholders must be a dict, {} given',format(type(extra_placeholders)))

        placeholders = extra_placeholders.copy()
        track_placeholders = {
            'title': self.title,
            'artist': self.artist,
            'album_artist': self.album_artist,
            'album_title': self.album_title,
            'composer': self.composer,
            'performer': self.performer,
            'comment': self.comment,
        }
        placeholders.update(track_placeholders)

        return Util.string_format(title_fmt, placeholders)

    def to_wav(self, output_file_name):
        """ Converts source audio track to WAV format

        convert source mp3 to wav. this is required for many reasons:
        * we need to adjust voice overlay amplitude to match MP3 file level and to do that we use "sox" too
          which cannot deal with MP3 directly.
        * there are some odd issues with "ffmpeg" failing during mixing phase when source is mp3 file.
          blind guess for now is that it's due to some structure mismatch between MP3 file (i.e. having cover
          image) and speech segments being just plain WAV. Most likely this can be solved better way but we
          need WAV anyway so no point wasting time at the moment for further research.
        """
        wav_cmd = ['ffmpeg', '-i', self.file_name, output_file_name]
        if Util.execute_rc(wav_cmd) != 0:
            raise RuntimeError('Failed to convert to WAV file')

    def get_encoding_quality_for_lame_encoder(self):
        """Selects LAME quality switch based on source file bitrate

           Based on https://trac.ffmpeg.org/wiki/Encode/MP3
        """
        quality = 0
        for avg in [245, 225, 190, 175, 165, 130, 115, 100, 85, 65]:
            if self.bitrate >= avg * 1000:
                break
            else:
                quality += 1

        return quality
