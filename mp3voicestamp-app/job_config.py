# coding=utf8

"""

 MP3 Voice Tag

 Athletes' companion: add synthetized voice overlay with various
 info and on-going timer to your audio files

 Copyright ©2018 Marcin Orlowski <mail [@] MarcinOrlowski.Com>

 https://github.com/MarcinOrlowski/mp3voicestamp

"""


class JobConfig(object):

    def __init__(self, args):
        self.args = args

        self.force_overwrite = args.force

        self.tick_pattern = args.tick_pattern
        self.tick_offset = args.tick_offset
        self.tick_interval = args.tick_interval
        self.tick_volume_factor = args.tick_volume_factor

        self.title_pattern = args.title_pattern
