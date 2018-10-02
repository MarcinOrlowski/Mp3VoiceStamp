# coding=utf8

"""

 MP3 Voice Stamp

 Athletes' companion: add synthetized voice overlay with various
 info and on-going timer to your audio files

 Copyright ©2018 Marcin Orlowski <mail [@] MarcinOrlowski.com>

 https://github.com/MarcinOrlowski/mp3voicestamp

"""


class JobConfig(object):
    DEFAULT_TITLE_PATTERN = '{title}'

    DEFAULT_SPEECH_SPEED = 150
    DEFAULT_SPEECH_VOLUME_FACTOR = 1

    DEFAULT_TICK_PATTERN = '{} minutes'
    DEFAULT_TICK_INTERVAL = 5
    DEFAULT_TICK_OFFSET = 5

    SPEECH_SPEED_MIN = 80
    SPEECH_SPEED_MAX = 450

    def __init__(self):
        self.force_overwrite = False

        self.speech_speed = JobConfig.DEFAULT_SPEECH_SPEED
        self.speech_volume_factor = JobConfig.DEFAULT_SPEECH_VOLUME_FACTOR

        self.tick_pattern = JobConfig.DEFAULT_TICK_PATTERN
        self.tick_interval = JobConfig.DEFAULT_TICK_INTERVAL
        self.tick_offset = JobConfig.DEFAULT_TICK_OFFSET

        self.title_pattern = JobConfig.DEFAULT_TITLE_PATTERN

        self.files_in = []
        self.file_out = None

    def set_tick_pattern(self, tick_pattern):
        tick_pattern = tick_pattern.strip()
        if tick_pattern == '':
            raise ValueError('Invalid tick pattern')
        self.tick_pattern = tick_pattern

    def set_tick_interval(self, tick_interval):
        if tick_interval < 1:
            raise ValueError('Tick Interval value cannot be shorter than 1 minute')
        self.tick_interval = tick_interval

    def set_tick_offset(self, tick_offset):
        if tick_offset < 1:
            raise ValueError.abort('Tick Offset value cannot be shorter than 1 minute')
        self.tick_offset = tick_offset

    def set_speech_volume_factor(self, speech_volume_factor):
        if speech_volume_factor <= 0:
            raise ValueError('Volume Factor must be non zero positive value')
        self.speech_volume_factor = speech_volume_factor

    def set_speech_speed(self, speech_speed):
        if speech_speed < JobConfig.SPEECH_SPEED_MIN or speech_speed > JobConfig.SPEECH_SPEED_MAX:
            raise ValueError(
                'Speech speed must be between {} and {}'.format(JobConfig.SPEECH_SPEED_MIN, JobConfig.SPEECH_SPEED_MAX))
        self.speech_speed = speech_speed

    def set_title_pattern(self, title_pattern):
        title_pattern = title_pattern.strip()
        if title_pattern == '':
            raise ValueError('Invalid title pattern')
        self.title_pattern = title_pattern

    def set_force_overwrite(self, val):
        self.force_overwrite = val

    # ----------------------

    def set_files_in(self, files_in):
        self.files_in = files_in

    def set_file_out(self, file_out):
        import os

        if len(self.files_in) > 1 and file_out is not None:
            file_out = file_out[0]
            if not os.path.isdir(file_out):
                raise ValueError('For multiple inputs, target must point to a directory, not to a file')

        self.file_out = file_out
