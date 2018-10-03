# coding=utf8

"""

 MP3 Voice Stamp

 Athletes' companion: add synthetized voice overlay with various
 info and on-going timer to your audio files

 Copyright ©2018 Marcin Orlowski <mail [@] MarcinOrlowski.com>

 https://github.com/MarcinOrlowski/mp3voicestamp

"""

import os
import ConfigParser


class JobConfig(object):
    INI_SECTION_NAME = 'mp3voicestamp'

    DEFAULT_TITLE_PATTERN = '{title}'

    DEFAULT_SPEECH_SPEED = 150
    DEFAULT_SPEECH_VOLUME_FACTOR = 1

    DEFAULT_TICK_PATTERN = '{} minutes'
    DEFAULT_TICK_INTERVAL = 5
    DEFAULT_TICK_OFFSET = 5

    DEFAULT_FILE_OUT_PATTERN = '{name} (voicestamped).{ext}'

    SPEECH_SPEED_MIN = 80
    SPEECH_SPEED_MAX = 450

    DEFAULT_CONFIG_FILE_NAME = 'default.ini'

    # *****************************************************************************************************************

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

        self.file_out_pattern = JobConfig.DEFAULT_FILE_OUT_PATTERN

    # *****************************************************************************************************************

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
            raise ValueError('Tick Offset value cannot be shorter than 1 minute')
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

    def set_title_pattern(self, pattern):
        pattern = pattern.strip()
        if pattern == '':
            raise ValueError('Invalid title pattern')
        self.title_pattern = pattern

    def set_force_overwrite(self, val):
        self.force_overwrite = val

    # *****************************************************************************************************************

    def set_files_in(self, files_in):
        self.files_in = files_in

    def set_file_out(self, file_out):

        import os
        if len(self.files_in) > 1 and file_out is not None:
            file_out = file_out
            if not os.path.isdir(file_out):
                raise ValueError('For multiple inputs, target must point to a directory, not to a file')

        self.file_out = file_out

    def set_file_out_pattern(self, pattern):
        if not isinstance(pattern, basestring):
            raise ValueError('Pattern must be a string. {} received.'.format(type(pattern)))
        pattern = pattern.strip()
        if pattern == '':
            raise ValueError('Invalid out file name pattern')
        self.file_out_pattern = pattern

    # *****************************************************************************************************************

    def _sanitize_string(self, string):
        if string[0:1] == '"':
            string = string[1:]
        if string[-1:] == '"':
            string = string[:-1]
        return string.strip()

    def load(self, file_name):
        """Load patch config file (if exists).

        Args:
          file_name: path to config file to load

        Returns:
          True if loading was successful, False if config file is missing. Raises exception on parse failure
        """
        result = False

        config_file_full = os.path.expanduser(file_name)

        if os.path.isfile(config_file_full):
            config = ConfigParser.ConfigParser()
            # custom optionxform prevents keys from being lower-cased (default implementation) as CaSe matters for us
            config.optionxform = str

            # noinspection PyBroadException
            config.read(config_file_full)

            section = self.INI_SECTION_NAME
            if config.has_option(section, 'file_out_pattern'):
                self.set_file_out_pattern(self._sanitize_string(config.get(section, 'file_out_pattern')))

            if config.has_option(section, 'speech_speed'):
                self.set_speech_speed(config.getint(section, 'speech_speed'))
            if config.has_option(section, 'speech_volume_factor'):
                self.set_speech_volume_factor(float(config.get(section, 'speech_volume_factor').replace(',', '.')))

            if config.has_option(section, 'title_pattern'):
                self.set_title_pattern(self._sanitize_string(config.get(section, 'title_pattern')))

            if config.has_option(section, 'tick_pattern'):
                self.set_tick_pattern(self._sanitize_string(config.get(section, 'tick_pattern')))
            if config.has_option(section, 'tick_offset'):
                self.set_tick_offset(config.getint(section, 'tick_offset'))
            if config.has_option(section, 'tick_offset'):
                self.set_tick_interval(config.getint(section, 'tick_interval'))

            result = True

        return result

    def save(self, file_name):
        """Dumps current configuration as INI file.

        Args:
          file_name: name of destination config file
        """
        file_name_full = os.path.expanduser(file_name)
        if os.path.exists(file_name_full) and not self.force_overwrite:
            raise IOError('File already exists. Use -f to force overwrite: {}.'.format(file_name))

        out_buffer = [
            '# Mp3VoiceStamp configuration file',
            '# https://github.com/MarcinOrlowski/mp3voicestamp',
            '',
            '[{}]'.format(self.INI_SECTION_NAME),
            self._prepare_config_entry('file_out_pattern', self.file_out_pattern),
            '',
            self._prepare_config_entry('speech_speed', self.speech_speed),
            self._prepare_config_entry('speech_volume_factor', self.speech_volume_factor),
            '',
            self._prepare_config_entry('title_pattern', self.title_pattern),
            '',
            self._prepare_config_entry('tick_pattern', self.tick_pattern),
            self._prepare_config_entry('tick_offset', self.tick_offset),
            self._prepare_config_entry('tick_interval', self.tick_interval),
        ]

        with open(file_name_full, "w+") as fh:
            fh.writelines('\n'.join(out_buffer))

    def _prepare_config_entry(self, ini_key, val):
        result = None

        if isinstance(val, (str, unicode)):
            result = '"{}"'.format(val)
        if isinstance(val, (int, float)):
            result = '{}'.format(val)

        if result is None:
            raise ValueError('Unknown type of %r' % ini_key)

        return '{} = {}'.format(ini_key, result)
