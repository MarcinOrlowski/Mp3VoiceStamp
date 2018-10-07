# coding=utf8

"""

 MP3 Voice Stamp

 Athletes' companion: adds synthetized voice overlay with various
 info and on-going timer to your audio files

 Copyright ©2018 Marcin Orlowski <mail [@] MarcinOrlowski.com>

 https://github.com/MarcinOrlowski/Mp3VoiceStamp

"""

# noinspection PyCompatibility
from past.builtins import basestring

import os

try:
    import configparser
except ImportError:
    import ConfigParser as configparser

from util import Util
from const import *


class Config(object):
    DEFAULT_TITLE_FORMAT = '{title} {config_name}'

    DEFAULT_SPEECH_SPEED = 150
    DEFAULT_SPEECH_VOLUME_FACTOR = 2

    DEFAULT_TICK_FORMAT = '{minutes} minutes'
    DEFAULT_TICK_INTERVAL = 5
    DEFAULT_TICK_OFFSET = 5

    DEFAULT_FILE_OUT_FORMAT = '{name} (mp3voicestamped).{ext}'

    SPEECH_SPEED_MIN = 80
    SPEECH_SPEED_MAX = 450

    # *****************************************************************************************************************

    INI_SECTION_NAME = 'mp3voicestamp'

    INI_KEY_FILE_OUT_FORMAT = 'file_out_format'

    INI_KEY_SPEECH_SPEED = 'speech_speed'
    INI_KEY_SPEECH_VOLUME_FACTOR = 'speech_volume_factor'

    INI_KEY_TITLE_FORMAT = 'title_format'

    INI_KEY_TICK_FORMAT = 'tick_format'
    INI_KEY_TICK_OFFSET = 'tick_offset'
    INI_KEY_TICK_INTERVAL = 'tick_interval'

    # *****************************************************************************************************************

    def __init__(self):
        self.name = ''

        self.force_overwrite = False
        self.dry_run_mode = False
        self.debug = False

        self.speech_speed = Config.DEFAULT_SPEECH_SPEED
        self.speech_volume_factor = Config.DEFAULT_SPEECH_VOLUME_FACTOR

        self.tick_format = Config.DEFAULT_TICK_FORMAT
        self.tick_interval = Config.DEFAULT_TICK_INTERVAL
        self.tick_offset = Config.DEFAULT_TICK_OFFSET

        self.title_format = Config.DEFAULT_TITLE_FORMAT

        self.files_in = []
        self.file_out = None

        self.file_out_format = Config.DEFAULT_FILE_OUT_FORMAT

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

            # noinspection PyCompatibility
            if not isinstance(value, basestring):
                value = str(value)

            if strip:
                value = value.strip()

        return value

    # *****************************************************************************************************************

    @property
    def tick_format(self):
        return self.__tick_format

    @tick_format.setter
    def tick_format(self, value):
        value = self.__get_as_string(value)
        if value is not None:
            self.__tick_format = value

    @property
    def tick_offset(self):
        return self.__tick_offset

    @tick_offset.setter
    def tick_offset(self, value):
        value = Config.__get_as_int(value)
        if value is not None:
            if value < 1:
                raise ValueError('Tick offset value cannot be shorter than 1 minute')

            self.__tick_offset = value

    @property
    def tick_interval(self):
        return self.__tick_interval

    @tick_interval.setter
    def tick_interval(self, value):
        value = Config.__get_as_int(value)
        if value is not None:
            if value < 1:
                raise ValueError('Tick interval value cannot be shorter than 1 minute')

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
                raise ValueError('Volume factor must be non zero positive value')

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
    def title_format(self):
        return self.__title_format

    @title_format.setter
    def title_format(self, value):
        value = Config.__get_as_string(value)
        if value is not None:
            self.__title_format = value

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
    def file_out_format(self):
        return self.__file_out_format

    @file_out_format.setter
    def file_out_format(self, value):
        value = Config.__get_as_string(value)
        if value is not None:
            if value == '':
                raise ValueError('Invalid out file name format string')
            self.__file_out_format = value

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
            config = configparser.ConfigParser()
            # custom optionxform prevents keys from being lower-cased (default implementation) as CaSe matters for us
            config.optionxform = str

            # noinspection PyBroadException
            config.read(config_file_full)

            section = self.INI_SECTION_NAME
            if config.has_option(section, self.INI_KEY_FILE_OUT_FORMAT):
                self.file_out_format = Config.__strip_quotes_from_ini_string(
                    config.get(section, self.INI_KEY_FILE_OUT_FORMAT))

            if config.has_option(section, self.INI_KEY_SPEECH_SPEED):
                self.speech_speed = config.getint(section, self.INI_KEY_SPEECH_SPEED)
            if config.has_option(section, self.INI_KEY_SPEECH_VOLUME_FACTOR):
                self.speech_volume_factor = config.get(section, self.INI_KEY_SPEECH_VOLUME_FACTOR).replace(',', '.')

            if config.has_option(section, self.INI_KEY_TITLE_FORMAT):
                self.title_format = Config.__strip_quotes_from_ini_string(
                    config.get(section, self.INI_KEY_TITLE_FORMAT))

            if config.has_option(section, self.INI_KEY_TICK_FORMAT):
                self.tick_format = Config.__strip_quotes_from_ini_string(config.get(section, self.INI_KEY_TICK_FORMAT))
            if config.has_option(section, self.INI_KEY_TICK_OFFSET):
                self.tick_offset = config.getint(section, self.INI_KEY_TICK_OFFSET)
            if config.has_option(section, self.INI_KEY_TICK_OFFSET):
                self.tick_interval = config.getint(section, self.INI_KEY_TICK_INTERVAL)

            name = os.path.basename(file_name)
            name = name[:-4] if name[-4:] == '.ini' else name
            self.name = Util.prepare_for_speak(name)

            result = True

        return result

    @staticmethod
    def __strip_quotes_from_ini_string(string):
        if string[0:1] == '"':
            string = string[1:]
        if string[-1:] == '"':
            string = string[:-1]
        return string.strip()

    # *****************************************************************************************************************

    @staticmethod
    def __format_ini_entry(ini_key, val):
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
            '# {} configuration file'.format(APP_NAME),
            '# {}'.format(APP_URL),
            '',
            '[{}]'.format(self.INI_SECTION_NAME),
            Config.__format_ini_entry(self.INI_KEY_FILE_OUT_FORMAT, self.file_out_format),
            '',
            Config.__format_ini_entry(self.INI_KEY_SPEECH_SPEED, self.speech_speed),
            Config.__format_ini_entry(self.INI_KEY_SPEECH_VOLUME_FACTOR, self.speech_volume_factor),
            '',
            Config.__format_ini_entry(self.INI_KEY_TITLE_FORMAT, self.title_format),
            '',
            Config.__format_ini_entry(self.INI_KEY_TICK_FORMAT, self.tick_format),
            Config.__format_ini_entry(self.INI_KEY_TICK_OFFSET, self.tick_offset),
            Config.__format_ini_entry(self.INI_KEY_TICK_INTERVAL, self.tick_interval),
        ]

        with open(file_name_full, 'w+') as fh:
            fh.writelines('\n'.join(out_buffer))
