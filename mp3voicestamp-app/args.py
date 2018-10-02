# coding=utf8

"""

 MP3 Voice Stamp

 Athletes' companion: add synthetized voice overlay with various
 info and on-going timer to your audio files

 Copyright ©2018 Marcin Orlowski <mail [@] MarcinOrlowski.com>

 https://github.com/MarcinOrlowski/mp3voicestamp

"""

import os
import argparse
from argparse import RawDescriptionHelpFormatter

from util import Util
from version import VERSION


class Args(object):
    """Handles command line arguments"""

    DEFAULT_TICK_PATTERN = '{} minutes'

    @staticmethod
    def parse_args():
        """Parses command line arguments

        :returns argsparse
        """
        parser = argparse.ArgumentParser(
            description='Adds spoken overlay to MP3 with title, time stamps and more.\n'
                        'Written by Marcin Orlowski <mail@marcinorlowski.com>\n'
                        'WWW: https://github.com/MarcinOrlowski/mp3voicestamp',
            formatter_class=RawDescriptionHelpFormatter)

        group = parser.add_argument_group('In/Out files')
        group.add_argument(
            '-i', '--in',
            metavar="MP3_FILE", action='store', dest="files_in", nargs='+', required=True,
            help="On or more source MP3 files"
        )
        group.add_argument(
            '-o', '--out',
            metavar="DIR/MP3_FILE", action='store', dest="file_out", nargs=1,
            required=False,
            help='Optional output file name or target directory. If not specified, file name will be generated.'
        )

        group = parser.add_argument_group('Universal switches')
        group.add_argument(
            '-f', '--force', action='store_true', dest='force',
            help='Forces overwrite of existing output file'
        )
        group.add_argument(
            '-v', '--verbose', action='store_true', dest='verbose',
            help='Makes app more verbose'
        )
        group.add_argument(
            '-q', '--quiet', action='store_true', dest='quiet',
            help='Mute all progress messages.')

        group = parser.add_argument_group('Track title speech')
        group.add_argument(
            '-t', '--title-pattern', action='store', dest='title_pattern', nargs=1,
            metavar='PATTERN', default="{title}", required=False,
            help='Pattern for track title voice overlay. See --title-help for more info')

        group = parser.add_argument_group('Spoken timer')
        group.add_argument(
            '-ti', '--tick-interval', action='store', type=int, dest='tick_interval', nargs=1,
            metavar='MINUTES', default=[5], required=False,
            help='Interval (in minutes) between spoken ticks')
        group.add_argument(
            '-to', '--tick-offset', action='store', type=int, dest='tick_offset', nargs=1,
            metavar='MINUTES', default=[5], required=False,
            help='Offset (in minutes) for first spoken tick')
        group.add_argument(
            '-tp', '--tick-pattern', action='store', dest='tick_pattern', nargs=1,
            metavar='PATTERN', default=[Args.DEFAULT_TICK_PATTERN], required=False,
            help='Pattern for spoken ticks with "{}" replaced with minute tick value')
        group.add_argument(
            '-tvf', '--tick-volume-factor', action='store', dest='tick_volume_factor', nargs=1,
            metavar='FLOAT', default=[1], required=False,
            help='Speech volume adjustment factor')

        group = parser.add_argument_group('Developer tools')
        group.add_argument(
            '-d', '--debug', action='store_true', dest='debug',
            help='Enables additional debug output')

        group = parser.add_argument_group('Misc')
        group.add_argument(
            '--version', action='version',
            version='%(prog)s Adds spoken overlay to MP3 with title and time stamps v{v}'.format(v=VERSION))

        args = parser.parse_args()

        # some post processing
        if len(args.files_in) > 1 and args.file_out is not None:
            args.file_out = args.file_out[0]
            if not os.path.isdir(args.file_out):
                Util.abort('For multiple inputs, target must point to directory, not a file')

        # noinspection PyUnresolvedReferences
        args.tick_volume_factor = float(args.tick_volume_factor[0])
        if args.tick_volume_factor <= 0:
            Util.abort('Tick Volume Factor must be non zero positive value')
        args.tick_interval = args.tick_interval[0]
        if args.tick_interval < 1:
            Util.abort('Tick Interval value cannot be shorter than 1 minute')
        args.tick_offset = args.tick_offset[0]
        if args.tick_offset < 1:
            Util.abort('Tick Offset value cannot be shorter than 1 minute')
        args.tick_pattern = args.tick_pattern[0].strip()
        if args.tick_pattern == '':
            args.tick_pattern = Args.DEFAULT_TICK_PATTERN

        return args
