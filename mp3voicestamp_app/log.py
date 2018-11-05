"""Logging module for BUILD file generator tool for depot3 to google3 project.

Logging module for BUILD file generator tool for depot3 to google3 automated
conversion project

Marcin Orlowski <orlowskim@google.com>
"""

from __future__ import print_function

import inspect
import re
import sys

import os


# ################################# LOG ##################################### #

class Log(object):
    """Action logging helper class.
    """

    # ###########################################################################

    # www.lihaoyi.com/post/BuildyourownCommandLinewithANSIescapecodes.html
    ANSI_BOLD = u'\u001b[1m'
    ANSI_UNDERLINE = u'\u001b[4m'
    ANSI_REVERSE = u'\u001b[7m'

    ANSI_BLACK = u'\u001b[30m'
    ANSI_BLACK_BRIGHT = u'\u001b[1;30m'
    ANSI_RED = u'\u001b[31m'
    ANSI_RED_BRIGHT = u'\u001b[1;31m'
    ANSI_GREEN = u'\u001b[32m'
    ANSI_GREEN_BRIGHT = u'\u001b[1;32m'
    ANSI_YELLOW = u'\u001b[33m'
    ANSI_YELLOW_BRIGHT = u'\u001b[1;33m'
    ANSI_BLUE = u'\u001b[34m'
    ANSI_BLUE_BRIGHT = u'\u001b[1;34m'
    ANSI_MAGENTA = u'\u001b[35m'
    ANSI_MAGENTA_BRIGHT = u'\u001b[1;35m'
    ANSI_CYAN = u'\u001b[36m'
    ANSI_CYAN_BRIGHT = u'\u001b[1;36m'
    ANSI_WHITE = u'\u001b[37m'
    ANSI_WHITE_BRIGHT = u'\u001b[1;37m'

    ANSI_BG_MAGENTA = u'\u001b[45m'
    ANSI_BG_CYAN = u'\u001b[46m'

    ANSI_RESET = u'\u001b[0m'

    COLOR_ERROR = ANSI_RED
    COLOR_WARN = ANSI_YELLOW
    COLOR_NOTICE = ANSI_CYAN
    COLOR_INFO = None
    COLOR_OK = ANSI_GREEN
    COLOR_DEBUG = ANSI_REVERSE
    COLOR_BANNER = (ANSI_WHITE + ANSI_REVERSE)

    COLOR_REPO = (ANSI_BG_CYAN + ANSI_BLACK)
    COLOR_LOCAL = (ANSI_REVERSE + ANSI_WHITE_BRIGHT)

    # ###########################################################################

    deferred_log_level = None
    deferred_log_entry = None
    last_log_entry_level = 0
    log_level = 0
    log_entries = []

    verbose_level = 0
    debug = False
    no_color = False
    quiet = False
    skip_empty_lines = False

    VERBOSE_NONE = 0
    VERBOSE_NORMAL = 1
    VERBOSE_VERY = 2

    @classmethod
    def configure(cls, config):
        verbose_level = Log.VERBOSE_NONE
        if config.verbose:
            verbose_level = Log.VERBOSE_NORMAL
        # if args.very_verbose:
        #     verbose_level = Log.VERBOSE_VERY
        cls.verbose_level = verbose_level

        cls.skip_empty_lines = False
        cls.debug = config.debug
        cls.no_color = False
        cls.quiet = False

        if config.debug and os.getenv('PYTHONDONTWRITEBYTECODE') is None:
            Log.e([
                'Creation of *.pyc files is enabled in your current env.',
                'This affects debug() calls and will produce invalid',
                'file name and line number being shown during execution.',

                'To disable this, set env variable:',
                '   export PYTHONDONTWRITEBYTECODE=1',
            ])

    # ###########################################################################

    @staticmethod
    def level_init(message=None, color=None, ignore_quiet_switch=False):
        Log.log_level = 0
        Log.level_push(message, color, ignore_quiet_switch)

    @staticmethod
    def level_push(message=None, color=None, ignore_quiet_switch=False, deferred=False):
        if Log.verbose_level == 0 and deferred:
            Log.__flush_deferred_entry()

            Log.deferred_log_level = Log.log_level
            Log.deferred_log_entry = Log.__format_log_line(message, color)
        else:
            Log.__log(message, color, ignore_quiet_switch)

        Log.log_level += 1

    @staticmethod
    def level_pop(messages=None, color=None, ignore_quiet_switch=False):
        if messages is not None:
            Log.i(messages=messages, color=color, ignore_quiet_switch=ignore_quiet_switch)

        Log.__flush_deferred_entry()

        if Log.log_level == 0:
            Log.abort('level_pop() called too many times')
        Log.log_level -= 1

    # ###########################################################################

    @staticmethod
    def banner(messages, ignore_quiet_switch=False, add_to_history=False):
        Log.__log(messages, Log.COLOR_BANNER,
                  ignore_quiet_switch, add_to_history)

    # info
    @staticmethod
    def i(messages=None, color=COLOR_INFO, ignore_quiet_switch=False, add_to_history=True):
        Log.__log(messages, color, ignore_quiet_switch, add_to_history)

    # notice
    @staticmethod
    def n(messages=None, color=COLOR_NOTICE, ignore_quiet_switch=False, add_to_history=True):
        Log.__log(messages, color, ignore_quiet_switch, add_to_history)

    # verbose
    @staticmethod
    def v(messages=None):
        if Log.verbose_level >= 1:
            Log.__log(messages)

    # very verbose
    @staticmethod
    def vv(messages=None):
        if Log.verbose_level >= 2:
            Log.__log(messages)

    # warning
    @staticmethod
    def w(message=None):
        if message is not None:
            messages = Log.__to_list(message)
            _ = [Log.__log('**WARN** ' + Log.strip_ansi(msg), Log.COLOR_WARN, True) for msg in messages]

    # error
    @staticmethod
    def e(messages=None):
        if messages is not None:
            messages = Log.__to_list(messages)
            _ = [Log.__log('*** ' + Log.strip_ansi(message), Log.COLOR_ERROR, True) for message in messages]

    # debug
    # NOTE: debug entries are not stored in action log
    @staticmethod
    def d(messages=None):
        if messages is not None and Log.debug:
            postfix = Log.__get_stacktrace_string()
            for message in Log.__to_list(messages):
                raw_msg = message + ' [DEBUG]'
                message = Log.__format_log_line(raw_msg, Log.COLOR_DEBUG, postfix)
                postfix = ''
                print(message)

    @staticmethod
    def get_entries():
        return Log.log_entries

    @staticmethod
    def abort(messages=None):
        Log.e(messages)
        Log.level_init('*** Aborted', Log.COLOR_ERROR, True)

        if Log.debug:
            Log.d('Related stacktrace below')
            raise RuntimeError(
                '*** IT DID NOT CRASH *** Exception raised because of --debug used to obtain stacktrace. Enjoy.')
        else:
            sys.exit(1)

    @staticmethod
    def __get_stacktrace_string():
        msg = ''
        if Log.debug:
            frames = inspect.stack()
            for offset in range(3, len(frames)):
                frame = frames[offset][0]
                info = inspect.getframeinfo(frame)
                if os.path.basename(info.filename) != os.path.basename(__file__):
                    msg = ' %black_bright%({file}:{line})%reset%'.format(
                        file=os.path.basename(info.filename), line=info.lineno)
                    msg = Log.substitute_ansi(msg)
                    break

        return msg

    @staticmethod
    def strip_ansi(message):
        """Removes all ANSI control codes from given message string

        Args:
          message: string to be processed

        Returns:
          message string witn ANSI codes striped or None
        """
        if message is not None:
            pattern = re.compile(r'\x1B\[[0-?]*[ -/]*[@-~]')
            return pattern.sub('', message)

        return ''

    @staticmethod
    def substitute_ansi(message):
        """Replaces color code placeholder with ANSI values.

        Args:
          message: message to process

        Returns:
          message with placeholders replaced with ANSI codes
        """
        color_map = {
            'reset': Log.ANSI_RESET,
            'reverse': Log.ANSI_REVERSE,

            'black': Log.ANSI_BLACK,
            'black_bright': Log.ANSI_BLACK_BRIGHT,
            'red': Log.ANSI_RED,
            'green': Log.ANSI_GREEN,
            'green_bright': Log.ANSI_GREEN_BRIGHT,
            'yellow': Log.ANSI_YELLOW,
            'yellow_bright': Log.ANSI_YELLOW_BRIGHT,
            'blue': Log.ANSI_BLUE,
            'magenta': Log.ANSI_MAGENTA,
            'cyan': Log.ANSI_CYAN,
            'white': Log.ANSI_WHITE,

            'error': Log.ANSI_RED,
            'warn': Log.ANSI_YELLOW,
            'notice': Log.ANSI_CYAN,
            'info': None,
            'ok': Log.ANSI_GREEN,
            'debug': Log.ANSI_REVERSE,
            'banner': (Log.ANSI_WHITE + Log.ANSI_REVERSE),
        }

        for (key, color) in color_map.items():
            message = re.sub('%{key}%'.format(key=key), color if color is not None else '', message)

        return message

    # ###########################################################################

    @staticmethod
    def __format_log_line(message=None, color=None, stacktrace_postfix=None):
        """Formats log message, adding required indentation and stuff.

        Args:
          message: message to format
          color: COLOR_xxx or ANSI_xxx color code to use if line should be colored
          stacktrace_postfix:

        Returns:
          Formatted log line
        """
        if message is not None:
            message = ' ' * (Log.log_level * 2) + Log.substitute_ansi(message)

            if Log.debug:
                message = '%d: %s' % (Log.log_level, message)

            if color is not None:
                message = color + message

            message += Log.ANSI_RESET

            if stacktrace_postfix is not None:
                message += stacktrace_postfix

            if Log.no_color:
                message = Log.strip_ansi(message)

        return message

    @staticmethod
    def __log(messages=None, color=None, ignore_quiet_switch=False, add_to_history=True):
        if messages is not None:
            Log.last_log_entry_level = Log.log_level
            Log.__flush_deferred_entry()

            postfix = Log.__get_stacktrace_string()
            for message in Log.__to_list(Log.__dict_to_list(messages, '%green%')):
                use_message = False if Log.skip_empty_lines and message else True
                if use_message:
                    message = Log.__format_log_line(message, color, postfix)
                    Log.__log_raw(message, ignore_quiet_switch, add_to_history)
                    postfix = ''

    @staticmethod
    def __log_raw(message=None, ignore_quiet_switch=False, add_to_history=True):
        if message is not None:
            if add_to_history:
                Log.log_entries.append(message)

            quiet = False if ignore_quiet_switch else Log.quiet
            if not quiet:
                print(message.rstrip())

    @staticmethod
    def __flush_deferred_entry():
        if Log.deferred_log_entry is not None:
            if Log.last_log_entry_level > Log.deferred_log_level:
                Log.__log_raw(Log.deferred_log_entry)

            Log.deferred_log_entry = None
            Log.deferred_log_level = None

        Log.last_log_entry_level = 0

    # Methods taken from Utils class

    @staticmethod
    def __to_list(data):
        """Converts certain data types (str, unicode) into list.

        Args:
          data: data to convert

        Returns:
          list with converted data
        """
        # variable types to be converted
        # noinspection PyCompatibility
        types = [basestring]

        for data_type in types:
            if isinstance(data, data_type):
                return [data]

        return data

    @staticmethod
    def __dict_to_list(data_to_convert, color=None):
        """Converts dictionary elements into list.

        Args:
          data_to_convert: dictionary to convert
          color: color code (i.e. '%red%' for each row)

        Returns:
          list with converted data.

        """
        if not isinstance(data_to_convert, dict):
            return data_to_convert

        array = []
        for (key, val) in data_to_convert.items():
            if color is not None:
                array.append('{color}{key}%reset% : {val}'.format(
                    color=color, key=key, val=val))
            else:
                array.append('%s: %s' % (key, val))
        return array
