# coding=utf8

"""

 MP3 Voice Stamp

 Athletes' companion: add synthetized voice overlay with various
 info and on-going timer to your audio files

 Copyright ©2018 Marcin Orlowski <mail [@] MarcinOrlowski.com>

 https://github.com/MarcinOrlowski/mp3voicestamp

"""

from __future__ import print_function

from args import Args
from util import Util
from job_config import JobConfig
from job import Job
from mutagen.mp3 import MutagenError


class App(object):

    @staticmethod
    def main():
        job_config = JobConfig()

        # parse common line arguments
        args = Args.parse_args(job_config)

        # init helper
        Util.init(args.quiet)

        # check runtime environment
        Util.check_env()

        for file_name in job_config.files_in:
            try:
                Job(job_config).voice_stamp(file_name)
            except MutagenError as ex:
                Util.print('*** ' + str(ex))
                continue
            except OSError as ex:
                Util.print('*** ' + str(ex))
                continue


# ---------------------------------------------------------------------------------

if __name__ == '__main__':
    App.main()
