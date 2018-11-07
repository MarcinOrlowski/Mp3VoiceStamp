# coding=utf8

"""

 MP3 Voice Stamp

 Athletes' companion: adds synthetized voice overlay with various
 info and on-going timer to your audio files

 Copyright ©2018 Marcin Orlowski <mail [@] MarcinOrlowski.com>

 https://github.com/MarcinOrlowski/Mp3VoiceStamp

"""

from __future__ import print_function

import os

from mutagen.mp3 import MP3
# noinspection PyProtectedMember
from mutagen.id3 import ID3, ID3NoHeaderError, TIT2, TALB, TPE1, TPE2, TCOM, TSSE, TOFN, TRCK

from mp3voicestamp_app.const import *
from mp3voicestamp_app.util import Util
from mp3voicestamp_app.tools import Tools


class Mp3FileInfo(object):
    # https://en.wikipedia.org/wiki/ID3
    TAG_TITLE = 'TIT2'
    TAG_ARTIST = 'TPE1'
    TAG_ALBUM_ARTIST = 'TPE2'
    TAG_ALBUM_TITLE = 'TALB'
    TAG_COMPOSER = 'TCOM'
    TAG_PERFORMER = 'TOPE'
    TAG_COMMENT = 'COMM::XXX:'
    TAG_TRACK_NUMBER = 'TRCK'

    TAG_SOFTWARE = 'TSSE'
    TAG_ORIGINAL_FILENAME = 'TOFN'

    # *****************************************************************************************************************

    def __init__(self, file_name, tools):
        """

        :param str file_name:
        :param Tools tools:
        """
        if not os.path.exists(file_name):
            raise OSError('File not found: "{name}"'.format(name=file_name))

        mp3 = MP3(file_name)

        base_name, _ = Util.split_file_name(file_name)
        self.base_name = base_name
        self.file_name = file_name

        # we round up duration to full minutes
        self.duration = mp3.info.length
        self.bitrate = mp3.info.bitrate

        # get track title either from tag, or from filename
        self.title = self.__get_tag(mp3, self.TAG_TITLE)
        self.artist = self.__get_tag(mp3, self.TAG_ARTIST)
        self.album_artist = self.__get_tag(mp3, self.TAG_ALBUM_ARTIST)
        self.album_title = self.__get_tag(mp3, self.TAG_ALBUM_TITLE)
        self.composer = self.__get_tag(mp3, self.TAG_COMPOSER)
        self.performer = self.__get_tag(mp3, self.TAG_PERFORMER)
        self.comment = self.__get_tag(mp3, self.TAG_COMMENT)
        self.track_number = self.__get_tag(mp3, self.TAG_TRACK_NUMBER)

        self.__tools = tools

    # *****************************************************************************************************************

    @property
    def duration(self):
        """

        :return:
        :rtype:int
        """
        return int(round(self.__duration / 60 + 0.5))

    @duration.setter
    def duration(self, value):
        self.__duration = value

    @property
    def bitrate(self):
        """

        :return:
        :rtype:int
        """
        return self.__bitrate

    @bitrate.setter
    def bitrate(self, value):
        """

        :param value:
        :return:
        """
        self.__bitrate = int(value)

    @property
    def title(self):
        """

        :return:
        :rtype:str
        """
        result = self.__title
        if self.__title == '':
            result = self.base_name
        return result

    @title.setter
    def title(self, value):
        """

        :param str value:
        :return:
        """
        self.__title = str(value).strip()

    @property
    def artist(self):
        """

        :return:
        :rtype:str
        """
        return self.__artist if self.__artist != '' else self.album_artist

    @artist.setter
    def artist(self, value):
        """

        :param str value:
        :return:
        """
        self.__artist = str(value).strip()

    @property
    def track_number(self):
        """

        :return:
        :rtype:str
        """
        return self.__track_number

    @track_number.setter
    def track_number(self, value):
        """

        :param str value:
        :return:
        """
        if value == '-1':
            value = ''

        self.__track_number = value

    # *****************************************************************************************************************

    @staticmethod
    def __get_tag(mp3, tag, default=''):
        return default if tag not in mp3 else str(mp3[tag])

    # *****************************************************************************************************************

    def get_placeholders(self):
        """Returns track related placeholders, populated from ID3 tags.

        :return:
        :rtype:dict
        """
        return {
            'file_name': self.base_name,
            'track_number': self.track_number,
            'title': self.title,
            'artist': self.artist,
            'album_artist': self.album_artist,
            'album_title': self.album_title,
            'composer': self.composer,
            'performer': self.performer,
            'comment': self.comment,
        }

    # *****************************************************************************************************************

    def get_wav_segment_file_name(self, segment_number):
        pass

    def to_wav_segments(self, segment_file_name_pattern, split_segment_minutes=0):
        """Converts source audio track to WAV format splitting into segments. This is required for many reasons:
        * we need to adjust voice overlay amplitude to match MP3 file level and to do that we use "sox" too
          which cannot deal with MP3 directly.
        * there are some odd issues with "ffmpeg" failing during mixing phase when source is mp3 file.
          blind guess for now is that it's due to some structure mismatch between MP3 file (i.e. having cover
          image) and speech segments being just plain WAV. Most likely this can be solved better way but we
          need WAV anyway so no point wasting time at the moment for further research.

        :param str segment_file_name_pattern:
        :param int split_segment_minutes:

        :return:

        :raises RuntimeError
        """
        wav_cmd = [self.__tools.get_tool(Tools.KEY_FFMPEG), '-i', self.file_name]

        if split_segment_minutes > 0:
            # https://www.ffmpeg.org/ffmpeg-formats.html#segment_002c-stream_005fsegment_002c-ssegment
            wav_cmd.extend([
                '-f', 'segment', '-segment_time', str(split_segment_minutes * 60),
                segment_file_name_pattern,
            ])
        else:
            # we need to ensure possible %d element in pattern is replaced by sanev alue
            wav_cmd.append(segment_file_name_pattern % 0)

        if Util.execute_rc(wav_cmd) != 0:
            raise RuntimeError('Failed to convert audio track to WAV file')

    # *****************************************************************************************************************

    def get_encoding_quality_for_lame(self):
        """Selects LAME quality switch based on source file bitrate

        Based on https://trac.ffmpeg.org/wiki/Encode/MP3
        :return: int
        """
        quality = 0
        for avg in [245, 225, 190, 175, 165, 130, 115, 100, 85, 65]:
            if self.bitrate >= avg * 1000:
                break
            else:
                quality += 1

        return quality

    # *****************************************************************************************************************

    def write_id3_tags(self, file_name, track_title):
        """Writes ID3 tags from out music file into given MP3 file

        :param str file_name:
        :param str track_title:
        :return:
        """
        try:
            tags = ID3(file_name)
        except ID3NoHeaderError:
            # Adding ID3 header
            tags = ID3()

        tags[self.TAG_TITLE] = TIT2(encoding=3, text=track_title)
        tags[self.TAG_ALBUM_TITLE] = TALB(encoding=3, text=self.album_title)
        tags[self.TAG_ALBUM_ARTIST] = TPE2(encoding=3, text=self.album_artist)
        tags[self.TAG_ARTIST] = TPE1(encoding=3, text=self.artist)
        tags[self.TAG_COMPOSER] = TCOM(encoding=3, text=self.composer)
        tags[self.TAG_TRACK_NUMBER] = TRCK(encoding=3, text=self.track_number)

        tags[self.TAG_ORIGINAL_FILENAME] = TOFN(encoding=3, text=self.file_name)
        tags[self.TAG_SOFTWARE] = TSSE(encoding=3, text='{app} v{v} {url}'.format(app=APP_NAME, v=VERSION, url=APP_URL))

        tags.save(file_name)
