# coding=utf8

"""

 MP3 Voice Stamp

 Athletes' companion: add synthetized voice overlay with various
 info and on-going timer to your audio files

 Copyright ©2018 Marcin Orlowski <mail [@] MarcinOrlowski.com>

 https://github.com/MarcinOrlowski/Mp3VoiceStamp

"""

from __future__ import print_function

import sys
from args import Args
from util import Util
from config import Config
from job import Job
from mutagen import MutagenError


class App(object):

    @staticmethod
    def main():
        rc = 0

        try:
            config = Config()

            # parse common line arguments
            args = Args.parse_args(config)

            # check runtime environment
            Util.check_env()

            if args.config_save_name is not None:
                config.save(args.config_save_name)
            else:
                batch_mode = len(config.files_in) > 1

                if config.dry_run_mode:
                    if batch_mode:
                        Util.print('Files to process: {}'.format(len(config.files_in)))
                    Util.print('Title format: "{}"'.format(config.title_format))
                    Util.print('Tick format: "{}"'.format(config.tick_format))
                    Util.print('Ticks interval {freq} mins, start offset: {offset} mins'.format(
                        freq=config.tick_interval, offset=config.tick_offset))
                    Util.print()

                for file_name in config.files_in:
                    try:
                        Job(config).voice_stamp(file_name)
                    except MutagenError as ex:
                        Util.print_error(ex)
                        if batch_mode:
                            Util.print()
                            continue
                        else:
                            rc = 1
                    except OSError as ex:
                        Util.print_error(ex)
                        if batch_mode:
                            Util.print()
                            continue
                        else:
                            rc = 1
        except (ValueError, IOError) as ex:
            Util.print_error(str(ex), False)
            rc = 1

        sys.exit(rc)


# ---------------------------------------------------------------------------------

if __name__ == '__main__':
    App.main()
