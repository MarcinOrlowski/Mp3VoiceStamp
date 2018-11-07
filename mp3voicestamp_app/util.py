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

from mp3voicestamp_app.log import Log


class Util(object):
    quiet = False

    @staticmethod
    def abort(message=None):
        if message is not None:
            Log.e(message)
        if message is None:
            print('*** Aborted')
        sys.exit(1)

    @staticmethod
    def execute_rc(cmd_list, working_dir=None):
        """

        :param list cmd_list:
        :param str|None working_dir:
        :return:
        """
        rc, _, _ = Util.execute(cmd_list, working_dir)
        return rc

    @staticmethod
    def execute(cmd_list, working_dir=None):
        """Executes commands from cmd_list changing CWD to working_dir.

        :param list cmd_list: list with command i.e. ['g4', '-option', ...]
        :param str|None working_dir: if not None working directory is set to it for cmd exec

        :return:
        :rtype:(int, list, list)
        """
        if working_dir:
            old_cwd = os.getcwd()
            os.chdir(working_dir)

        Log.d('Executing: {}'.format(' '.join(cmd_list)))

        p = Popen(cmd_list, stdin=PIPE, stdout=PIPE, stderr=PIPE)
        stdout, err = p.communicate(None)
        rc = p.returncode

        if rc != 0:
            Log.i([
                'Command',
                '=======',
                ' '.join(cmd_list),
            ])

            if stdout.splitlines():
                Log.i([
                    'Command output (stdout)',
                    '=======================',
                ])
                _ = [Log.i('%r' % line) for line in stdout.splitlines()]

            if err.splitlines():
                Log.i([
                    'Command output (stderr)',
                    '=======================',
                ])
                _ = [Log.i('%r' % line) for line in err.splitlines()]

        # if rc != 0:
        #     print('Command output (stderr)')
        #     [Log.i('%r' % line) for line in err.splitlines()]

        if working_dir:
            # noinspection PyUnboundLocalVariable
            os.chdir(old_cwd)

        return rc, stdout.splitlines(), err.splitlines()

    @staticmethod
    def which(program):
        """Looks for given file (usually binary, executable) in known locations, incl. PATH

        :param str program:

        :return:Returns full path to known location of given executable or None
        :rtype:str:
        """

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
    def prepare_for_speak(text):
        """Tries to process provided text for more natural sound when spoken, i.e.
        "Track 013" => "Track 13" so no leading zero will be spoken (sorry James...).
        We also replace '-' by coma, to enforce small pause in spoken text

        :param str text:
        :return:
        :rtype:str
        """

        def strip_leading_zeros(re_match):
            return str(int(re_match.group(0)))

        return re.sub('\d{2,}', strip_leading_zeros, re.sub(' +', ' ', text).replace('-', ',')).strip()

    @staticmethod
    def separate_chars(text, sep=' '):
        """

        :param str text:
        :param str sep:
        :return:
        :rtype:str
        """
        result = ''
        text = str(text).strip()
        if text:
            for i in range(0, len(text)):
                result += text[i:i + 1] + sep

        return result

    @staticmethod
    def merge_dicts(dict1, dict2):
        """Merge two dictionaries
        
        :param dict dict1: base merge dictionary
        :param dict dict2: this dict is merged into dict1

        :return: dictionary with merged values. In case of key conflict, dictionary dict2 overwrites dict1 entry
        :rtype:dict
        """
        res = dict1.copy()
        res.update(dict2)

        return res

    @staticmethod
    def process_placeholders(fmt, placeholders, error_return_value=''):
        """

        :param str fmt:
        :param dict placeholders:
        :param str error_return_value:

        :return:
        :rtype:str
        """
        if fmt is None:
            return error_return_value

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
        """

        :param str file_name:
        :return:
        :rtype:(str, str)
        """
        base, ext = os.path.splitext(os.path.basename(file_name))
        ext = ext[1:] if ext[0:1] == '.' else ext

        return base, ext
