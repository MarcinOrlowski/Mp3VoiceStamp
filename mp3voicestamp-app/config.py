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
from util import Util


class Config(object):
    INI_SECTION_NAME = 'mp3voicestamp'

    DEFAULT_TITLE_PATTERN = '{title}'

    DEFAULT_SPEECH_SPEED = 150
    DEFAULT_SPEECH_VOLUME_FACTOR = 1

    DEFAULT_TICK_PATTERN = '{minutes} minutes'
    DEFAULT_TICK_INTERVAL = 5
    DEFAULT_TICK_OFFSET = 5

    DEFAULT_FILE_OUT_PATTERN = '{name} (voicestamped).{ext}'

    SPEECH_SPEED_MIN = 80
    SPEECH_SPEED_MAX = 450

    DEFAULT_CONFIG_FILE_NAME = 'default.ini'

    # *****************************************************************************************************************

    def __init__(self):
        self.name = ''

        self.force_overwrite = False

        self.speech_speed = Config.DEFAULT_SPEECH_SPEED
        self.speech_volume_factor = Config.DEFAULT_SPEECH_VOLUME_FACTOR

        self.tick_pattern = Config.DEFAULT_TICK_PATTERN
        self.tick_interval = Config.DEFAULT_TICK_INTERVAL
        self.tick_offset = Config.DEFAULT_TICK_OFFSET

        self.title_pattern = Config.DEFAULT_TITLE_PATTERN

        self.files_in = []
        self.file_out = None

        self.file_out_pattern = Config.DEFAULT_FILE_OUT_PATTERN

    # *****************************************************************************************************************

    @property
    def name(self):
        return self.__name

    @name.setter
    def name(self, value):
        self.__name = str(value)

    # *****************************************************************************************************************

    @staticmethod
    def __get_as_int(value):
        if value is not None:
            if isinstance(value, list):
                if not value:
                    raise ValueError('List cannot be empty')
                value = value[0]

            if not isinstance(value, int):
                value = int(value)

        return value

    @staticmethod
    def __get_as_float(value):
        if value is not None:
            if isinstance(value, list):
                if not value:
                    raise ValueError('List cannot be empty')
                value = value[0]

            if not isinstance(value, float):
                value = float(value)

        return value

    @staticmethod
    def __get_as_string(value, strip=True):
        if value is not None:
            if isinstance(value, list):
                if not value:
                    raise ValueError('List cannot be empty')
                value = value[0]

            if not isinstance(value, basestring):
                value = str(value)

            if strip:
                value = value.strip()

        return value

    # *****************************************************************************************************************

    @property
    def tick_pattern(self):
        return self.__tick_pattern

    @tick_pattern.setter
    def tick_pattern(self, value):
        value = self.__get_as_string(value)
        if value is not None:
            if value == '':
                raise ValueError('Invalid tick pattern')

            self.__tick_pattern = value

    @property
    def tick_offset(self):
        return self.__tick_offset

    @tick_offset.setter
    def tick_offset(self, value):
        value = Config.__get_as_int(value)
        if value is not None:
            if value < 1:
                raise ValueError('Tick Offset value cannot be shorter than 1 minute')

            self.__tick_offset = value

    @property
    def tick_interval(self):
        return self.__tick_interval

    @tick_interval.setter
    def tick_interval(self, value):
        value = Config.__get_as_int(value)
        if value is not None:
            if value < 1:
                raise ValueError('Tick Interval value cannot be shorter than 1 minute')

            self.__tick_interval = value

    # *****************************************************************************************************************

    @property
    def speech_volume_factor(self):
        return self.__speech_volume_factor

    @speech_volume_factor.setter
    def speech_volume_factor(self, value):
        value = Config.__get_as_float(value)
        if value is not None:
            if value <= 0:
                raise ValueError('Volume Factor must be non zero positive value')

            self.__speech_volume_factor = value

    @property
    def speech_speed(self):
        return self.__speech_speed

    @speech_speed.setter
    def speech_speed(self, value):
        value = Config.__get_as_int(value)
        if value is not None:
            if value < Config.SPEECH_SPEED_MIN or value > Config.SPEECH_SPEED_MAX:
                raise ValueError('Speech speed must be between {} and {}'.format(Config.SPEECH_SPEED_MIN,
                                                                                 Config.SPEECH_SPEED_MAX))
            self.__speech_speed = value

    # *****************************************************************************************************************

    @property
    def title_pattern(self):
        return self.__title_pattern

    @title_pattern.setter
    def title_pattern(self, value):
        value = Config.__get_as_string(value)
        if value is not None:
            if value == '':
                raise ValueError('Invalid title pattern')

            self.__title_pattern = value

    # *****************************************************************************************************************

    @property
    def force_overwrite(self):
        return self.__force_overwrite

    @force_overwrite.setter
    def force_overwrite(self, value):
        if value is not None and isinstance(value, bool):
            self.__force_overwrite = value

    # *****************************************************************************************************************

    @property
    def files_in(self):
        return self.__files_in

    @files_in.setter
    def files_in(self, value):
        if value is not None:
            self.__files_in = value

    # *****************************************************************************************************************

    @property
    def file_out(self):
        return self.__file_out

    @file_out.setter
    def file_out(self, file_out):
        file_out = Config.__get_as_string(file_out, False)
        if file_out is not None:
            if len(self.__files_in) > 1 and file_out is not None and not os.path.isdir(file_out):
                raise ValueError('For multiple inputs, target must point to a directory')

        self.__file_out = file_out

    @property
    def file_out_pattern(self):
        return self.__file_out_pattern

    @file_out_pattern.setter
    def file_out_pattern(self, value):
        value = Config.__get_as_string(value)
        if value is not None:
            if value == '':
                raise ValueError('Invalid out file name pattern')
            self.__file_out_pattern = value

    # *****************************************************************************************************************

    def load(self, file_name):
        """Load patch config file (if exists).

        Args:
          file_name: path to config file to load or None

        Returns:
          True if loading was successful, False if config file is missing. Raises exception on parse failure
        """
        result = False

        if file_name is None:
            return result

        config_file_full = os.path.expanduser(file_name)

        if os.path.isfile(config_file_full):
            config = ConfigParser.ConfigParser()
            # custom optionxform prevents keys from being lower-cased (default implementation) as CaSe matters for us
            config.optionxform = str

            # noinspection PyBroadException
            config.read(config_file_full)

            section = self.INI_SECTION_NAME
            if config.has_option(section, 'file_out_pattern'):
                self.file_out_pattern = self.__strip_quotes_from_ini_string(config.get(section, 'file_out_pattern'))

            if config.has_option(section, 'speech_speed'):
                self.speech_speed = config.getint(section, 'speech_speed')
            if config.has_option(section, 'speech_volume_factor'):
                self.speech_volume_factor = config.get(section, 'speech_volume_factor').replace(',', '.')

            if config.has_option(section, 'title_pattern'):
                self.title_pattern = self.__strip_quotes_from_ini_string(config.get(section, 'title_pattern'))

            if config.has_option(section, 'tick_pattern'):
                self.tick_pattern = self.__strip_quotes_from_ini_string(config.get(section, 'tick_pattern'))
            if config.has_option(section, 'tick_offset'):
                self.tick_offset = config.getint(section, 'tick_offset')
            if config.has_option(section, 'tick_offset'):
                self.tick_interval = config.getint(section, 'tick_interval')

            name = os.path.basename(file_name)
            name = name[:-4] if name[-4:] == '.ini' else name
            self.name = Util.prepare_for_speak(name)

            result = True

        return result

    # noinspection PyMethodMayBeStatic
    def __strip_quotes_from_ini_string(self, string):
        if string[0:1] == '"':
            string = string[1:]
        if string[-1:] == '"':
            string = string[:-1]
        return string.strip()

    # *****************************************************************************************************************

    # noinspection PyMethodMayBeStatic,PyMethodMayBeStatic
    def __prepare_config_entry(self, ini_key, val):
        result = None

        if isinstance(val, (str, unicode)):
            result = '"{}"'.format(val)
        if isinstance(val, (int, float)):
            result = '{}'.format(val)

        if result is None:
            raise ValueError('Unknown type of %r' % ini_key)

        return '{} = {}'.format(ini_key, result)

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
            self.__prepare_config_entry('file_out_pattern', self.file_out_pattern),
            '',
            self.__prepare_config_entry('speech_speed', self.speech_speed),
            self.__prepare_config_entry('speech_volume_factor', self.speech_volume_factor),
            '',
            self.__prepare_config_entry('title_pattern', self.title_pattern),
            '',
            self.__prepare_config_entry('tick_pattern', self.tick_pattern),
            self.__prepare_config_entry('tick_offset', self.tick_offset),
            self.__prepare_config_entry('tick_interval', self.tick_interval),
        ]

        with open(file_name_full, 'w+') as fh:
            fh.writelines('\n'.join(out_buffer))
