# coding=utf8

"""

 MP3 Voice Stamp

 Athletes' companion: add synthetized voice overlay with various
 info and on-going timer to your audio files

 Copyright ©2018 Marcin Orlowski <mail [@] MarcinOrlowski.com>

 https://github.com/MarcinOrlowski/mp3voicestamp

"""

import argparse
from argparse import RawDescriptionHelpFormatter

from config import Config
from version import VERSION


class Args(object):
    """Handles command line arguments"""

    @staticmethod
    def parse_args(job_config):
        """Parses command line arguments

        :returns argsparse
        """
        parser = argparse.ArgumentParser(
            description='Adds spoken overlay to MP3 with title, time stamps and more.\n'
                        'Written by Marcin Orlowski <mail@marcinOrlowski.com>\n'
                        'WWW: https://github.com/MarcinOrlowski/Mp3VoiceStamp',
            formatter_class=RawDescriptionHelpFormatter)

        group = parser.add_argument_group('In/Out files')
        group.add_argument(
            '-i', '--in',
            metavar="MP3_FILE", action='store', dest="files_in", nargs='+',
            help="On or more source MP3 files"
        )
        group.add_argument(
            '-o', '--out',
            metavar="DIR/MP3_FILE", action='store', dest="file_out", nargs=1,
            help='Optional output file name or target directory if "-in" option used with multiple files. ' +
                 'If not specified, file name will be generated.'
        )
        group.add_argument(
            '-op', '--out-pattern', action='store', dest='file_out_pattern', nargs=1, metavar='PATTERN',
            help='Pattern used to generate name of output. Default is "{}". '.format(Config.DEFAULT_FILE_OUT_PATTERN) +
                 'See docs for available placeholders.')

        group = parser.add_argument_group('Track title speech')
        group.add_argument(
            '-t', '--title-pattern', action='store', dest='title_pattern', nargs=1, metavar='PATTERN',
            help='Pattern for track title voice overlay. Default is "{}". '.format(Config.DEFAULT_TITLE_PATTERN) +
                 'See docs for available placeholders.')

        group = parser.add_argument_group('Spoken timer')
        group.add_argument(
            '-ti', '--tick-interval', action='store', type=int, dest='tick_interval', nargs=1, metavar='MINUTES',
            help='Interval (in minutes) between spoken ticks. Default is {}.'.format(Config.DEFAULT_TICK_INTERVAL))
        group.add_argument(
            '-to', '--tick-offset', action='store', type=int, dest='tick_offset', nargs=1, metavar='MINUTES',
            help='Offset (in minutes) for first spoken tick. Default is {}.'.format(Config.DEFAULT_TICK_OFFSET))
        group.add_argument(
            '-tp', '--tick-pattern', action='store', dest='tick_pattern', nargs=1, metavar='PATTERN',
            help='Pattern for spoken ticks with "{}" replaced with minute tick value.')

        group = parser.add_argument_group('Voice synthesizer')
        group.add_argument(
            '-sv', '--speech-volume', action='store', dest='speech_volume_factor', nargs=1, metavar='FLOAT',
            help='Speech volume adjustment multiplier, relative to calculated value. ' +
                 'I.e. "0.5" would lower the volume 50%%, while "2" boost it up to make it twice as loud ' +
                 'as it would be by default. Default is {}.'.format(Config.DEFAULT_SPEECH_VOLUME_FACTOR))
        group.add_argument(
            '-ss', '--speech-speed', action='store', dest='speech_speed', nargs=1, type=int, metavar='INTEGER',
            help='Speech speed in words per minute, in range from {} to {}. Default is {}.'.format(
                Config.SPEECH_SPEED_MIN, Config.SPEECH_SPEED_MAX, Config.DEFAULT_SPEECH_SPEED))

        group = parser.add_argument_group('Configuration')
        group.add_argument(
            '-c', '--config', action='store', dest='config_name', metavar='INI_FILE',
            help='Name of (optional) configuration file to load. If not specified, defaults will be used.'
        )

        group.add_argument(
            '-cs', '--config-save', action='store', dest='config_save_name', metavar='INI_FILE',
            help='Name of configuration file to dump current configuration to.'
        )

        group = parser.add_argument_group('Misc')
        group.add_argument(
            '-f', '--force', action='store_true', dest='force',
            help='Forces overwrite of existing output file'
        )
        group.add_argument(
            '-q', '--quiet', action='store_true', dest='quiet',
            help='Mutes all messages.'
        )
        group.add_argument(
            '-v', '--verbose', action='store_true', dest='verbose',
            help='Makes app more verbose'
        )
        group.add_argument(
            '--version', action='version',
            version='%(prog)s Adds speech overlay to your music file track title and time stamps v{v}'.format(
                v=VERSION))

        args = parser.parse_args()

        if args.files_in is None and args.config_save_name is None:
            parser.print_usage()
            raise ValueError('You must provide at least one mp3 file.')

        job_config.load(args.config_name)

        job_config.force_overwrite = args.force

        job_config.speech_volume_factor = args.speech_volume_factor
        job_config.speech_speed = args.speech_speed

        job_config.tick_interval = args.tick_interval
        job_config.tick_offset = args.tick_offset
        job_config.tick_pattern = args.tick_pattern

        job_config.title_pattern = args.title_pattern

        # other settings
        job_config.quiet = args.quiet

        job_config.files_in = args.files_in

        job_config.file_out = args.file_out
        job_config.file_out_pattern = args.file_out_pattern

        return args
