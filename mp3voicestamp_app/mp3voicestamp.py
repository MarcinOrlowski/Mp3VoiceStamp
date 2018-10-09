# coding=utf8

"""

 MP3 Voice Stamp

 Athletes' companion: adds synthetized voice overlay with various
 info and on-going timer to your audio files

 Copyright ©2018 Marcin Orlowski <mail [@] MarcinOrlowski.com>

 https://github.com/MarcinOrlowski/Mp3VoiceStamp

"""

from __future__ import print_function

import sys
from mp3voicestamp_app.args import Args
from mp3voicestamp_app.util import Util
from mp3voicestamp_app.config import Config
from mp3voicestamp_app.job import Job
from mp3voicestamp_app.tools import Tools
from mp3voicestamp_app.const import *

from mutagen import MutagenError


class App(object):

    @staticmethod
    def main():
        rc = 0

        config = Config()

        Util.print(['{app} v{v} by Marcin Orlowski <{e}>'.format(app=APP_NAME, v=VERSION, e=APP_EMAIL),
                    APP_URL,
                    ''
                    ])
        try:
            # parse common line arguments
            args = Args.parse_args(config)

            # check runtime environment
            tools = Tools()
            tools.check_env()

            if args.config_save_name is not None:
                config.save(args.config_save_name)
            else:
                batch_mode = len(config.files_in) > 1

                if config.dry_run_mode and config.files_in and batch_mode:
                    Util.print([
                        'Files to process: {}'.format(len(config.files_in)),
                        'Title format: "{}"'.format(config.title_format),
                        'Tick format: "{}"'.format(config.tick_format),
                        'Ticks interval {freq} mins, start offset: {offset} mins'.format(freq=config.tick_interval, offset=config.tick_offset),
                    ])
                    Util.print()

                for file_name in config.files_in:
                    try:
                        Job(config, tools).voice_stamp(file_name)
                    except MutagenError as ex:
                        if not config.debug:
                            Util.print_error(ex)
                            if batch_mode:
                                Util.print()
                                continue
                            else:
                                rc = 1
                        else:
                            raise
                    except OSError as ex:
                        if not config.debug:
                            Util.print_error(ex)
                            if batch_mode:
                                Util.print()
                                continue
                            else:
                                rc = 1
                        else:
                            raise
        except (ValueError, IOError) as ex:
            if not config.debug:
                Util.print_error(str(ex), False)
                rc = 1
            else:
                raise

        sys.exit(rc)


# ---------------------------------------------------------------------------------

if __name__ == '__main__':
    App.main()
