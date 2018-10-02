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
import sys
from subprocess import Popen, PIPE


class Util(object):
    quiet = True

    @classmethod
    def init(cls, quiet):
        cls.quiet = quiet

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
    def abort(message=None):
        if message is not None:
            print('*** {}'.format(message))
        if message is None:
            print('*** Aborted')
        sys.exit(1)

    @staticmethod
    def key_to_label(key):
        tmp = key.replace('_', ' ')
        return tmp[0:1].upper() + tmp[1:]

    @staticmethod
    def execute_rc(cmd_list, working_dir=None):
        rc, stdout, err = Util.execute(cmd_list, working_dir)
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
    def print_info(info_dict, title=None, quiet=None):
        from itertools import imap

        if quiet is None:
            quiet = Util.quiet

        if title is not None:
            Util.print(title, quiet)
            Util.print('=' * len(title), quiet)
        # print out what we collected
        label_len = max(imap(len, info_dict))

        for key, value in info_dict.items():
            Util.print('  %*s: %s' % (label_len, Util.key_to_label(key), value), quiet)
        Util.print(quiet=quiet)

    @staticmethod
    def which(program):
        def is_exe(full_path):
            return os.path.isfile(full_path) and os.access(full_path, os.X_OK)

        fpath, fname = os.path.split(program)
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
        tools = ['ffmpeg', 'normalize-audio', 'espeak', 'sox']
        for tool in tools:
            if Util.which(tool) is None:
                Util.abort('"{}" not found. See README.md for details.'.format(tool))
