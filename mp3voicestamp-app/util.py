# coding=utf8

"""

 MP3 Voice Stamp

 Athletes' companion: adds synthetized voice overlay with various
 info and on-going timer to your audio files

 Copyright ©2018 Marcin Orlowski <mail [@] MarcinOrlowski.com>

 https://github.com/MarcinOrlowski/Mp3VoiceStamp

"""

from __future__ import print_function
# noinspection PyCompatibility
from past.builtins import basestring

import os
import sys
from subprocess import Popen, PIPE
import re


class Util(object):
    quiet = False

    @staticmethod
    def print_no_lf(message, quiet=None):
        if quiet is None:
            quiet = Util.quiet

        if not quiet:
            print('{}: '.format(message), end='')
            sys.stdout.flush()

    @staticmethod
    def print(message='', quiet=None):
        if quiet is None:
            quiet = Util.quiet

        if not quiet:
            print(message)

    @staticmethod
    def print_error(message='', quiet=None):
        Util.print('*** {}'.format(str(message)), quiet)

    @staticmethod
    def abort(message=None):
        if message is not None:
            Util.print_error(message)
        if message is None:
            print('*** Aborted')
        sys.exit(1)

    @staticmethod
    def execute_rc(cmd_list, working_dir=None):
        rc, _, _ = Util.execute(cmd_list, working_dir)
        return rc

    @staticmethod
    def execute(cmd_list, working_dir=None):
        """Executes commands from cmd_list changing CWD to working_dir.

        Args:
          cmd_list: list with command i.e. ['g4', '-option', ...]
          working_dir: if not None working directory is set to it for cmd exec

        Returns: rc of executed command (usually 0 == success)
        """
        if working_dir:
            old_cwd = os.getcwd()
            os.chdir(working_dir)

        p = Popen(cmd_list, stdin=PIPE, stdout=PIPE, stderr=PIPE)
        stdout, err = p.communicate(None)
        rc = p.returncode

        if rc != 0:
            print('Command')
            print('=======')
            print(' '.join(cmd_list))

            if stdout.splitlines():
                print('Command output (stdout)')
                print('=======================')
                _ = [print('%r' % line) for line in stdout.splitlines()]

            if err.splitlines():
                print('Command output (stderr)')
                print('=======================')
                _ = [print('%r' % line) for line in err.splitlines()]

        # if rc != 0:
        #     print('Command output (stderr)')
        #     [print('%r' % line) for line in err.splitlines()]

        if working_dir:
            # noinspection PyUnboundLocalVariable
            os.chdir(old_cwd)

        return rc, stdout.splitlines(), err.splitlines()

    @staticmethod
    def which(program):
        def is_exe(full_path):
            return os.path.isfile(full_path) and os.access(full_path, os.X_OK)

        fpath, _ = os.path.split(program)
        if fpath:
            if is_exe(program):
                return program
        else:
            for path in os.environ["PATH"].split(os.pathsep):
                exe_file = os.path.join(path, program)
                if is_exe(exe_file):
                    return exe_file

        return None

    @staticmethod
    def check_env():
        """Checks if all external tools we need are already available and in $PATH
        """
        tools = [
            'ffmpeg',
            'normalize-audio',
            'espeak',
            'sox',
        ]
        for tool in tools:
            if Util.which(tool) is None:
                Util.abort('"{}" not found. See README.md for details.'.format(tool))

    @staticmethod
    def prepare_for_speak(text):
        """ Tries to process provided text for more natural sound when spoken, i.e.
            "Track 013" => "Track 13" so no leading zero will be spoken (sorry James...).
            We also replace '-' by coma, to enforce small pause in spoken text
        """

        def strip_leading_zeros(re_match):
            return str(int(re_match.group(0)))

        return re.sub('\d{2,}', strip_leading_zeros, re.sub(' +', ' ', text).replace('-', ',')).strip()

    @staticmethod
    def merge_dicts(dict1, dict2):
        """Merge two dictionaries

        :type dict1: dict
        :type dict2: dict
        """
        res = dict2.copy()
        res.update(dict1)

        return res

    @staticmethod
    def process_placeholders(fmt, placeholders):
        """

        :param fmt:
        :param placeholders:

        :type fmt: basestring
        :type placeholders: dict

        :return:
        """
        # noinspection PyCompatibility
        if not isinstance(fmt, basestring):
            raise ValueError('Format must be a string, {} given'.format(type(fmt)))
        if not isinstance(placeholders, dict):
            raise ValueError('Placeholders must be a dict, {} given'.format(type(placeholders)))

        for key, val in placeholders.items():
            fmt = fmt.replace('{' + key + '}', str(val))

        return fmt

    @staticmethod
    def split_file_name(file_name):
        base, ext = os.path.splitext(os.path.basename(file_name))
        ext = ext[1:] if ext[0:1] == '.' else ext

        return base, ext
