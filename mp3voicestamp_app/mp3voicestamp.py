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
from mp3voicestamp_app.config import Config
from mp3voicestamp_app.job import Job
from mp3voicestamp_app.tools import Tools
from mp3voicestamp_app.const import *
from mp3voicestamp_app.log import Log

from mutagen import MutagenError


class App(object):

    @staticmethod
    def main():
        rc = 0

        config = Config()

        try:
            # parse common line arguments
            args = Args.parse_args(config)

            Log.i(['{app} v{v} by Marcin Orlowski <{e}>'.format(app=APP_NAME, v=VERSION, e=APP_EMAIL),
                   APP_URL,
                   ''
                   ])

            Log.configure(config)

            # check runtime environment
            tools = Tools()
            tools.check_env()

            if args.config_save_name is not None:
                config.save(args.config_save_name)
            else:
                batch_mode = len(config.files_in) > 1

                if config.dry_run_mode and config.files_in and batch_mode:
                    Log.i([
                        'Files to process: {}'.format(len(config.files_in)),
                        'Title format: "{}"'.format(config.title_format),
                        'Tick format: "{}"'.format(config.tick_format),
                        'Ticks interval {freq} mins, start offset: {offset} mins'.format(freq=config.tick_interval,
                                                                                         offset=config.tick_offset),
                        '',
                    ])

                for file_name in config.files_in:
                    try:
                        Job(config, tools).voice_stamp(file_name)
                    except MutagenError as ex:
                        if not config.debug:
                            Log.e(ex)
                            if batch_mode:
                                Log.i()
                                continue
                            else:
                                rc = 1
                        else:
                            raise
                    except OSError as ex:
                        if not config.debug:
                            Log.e(ex)
                            if batch_mode:
                                Log.i()
                                continue
                            else:
                                rc = 1
                        else:
                            raise
        except (ValueError, IOError) as ex:
            if not config.debug:
                Log.e(str(ex))
                rc = 1
            else:
                raise

        sys.exit(rc)


# ---------------------------------------------------------------------------------

if __name__ == '__main__':
    App.main()
