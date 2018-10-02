# coding=utf8

"""

 MP3 Voice Tag

 Athletes' companion: add synthetized voice overlay with various
 info and on-going timer to your audio files

 Copyright ©2018 Marcin Orlowski <mail [@] MarcinOrlowski.Com>

 https://github.com/MarcinOrlowski/mp3voicestamp

"""

from __future__ import print_function

from args import Args
from util import Util
from job_config import JobConfig
from job import Job
from mutagen.mp3 import MP3, MutagenError


class App(object):

    def main(self):
        # parse common line arguments
        args = Args.parse_args()
        Util.init(args)

        # check runtime environment
        Util.check_env()

        job_config = JobConfig(args)
        for file_in in args.files_in:
            try:
                Job(job_config).voice_stamp(file_in)
            except MutagenError as ex:
                Util.print('*** ' + str(ex))
                continue
            except OSError as ex:
                Util.print('*** ' + str(ex))
                continue


# ---------------------------------------------------------------------------------

if __name__ == '__main__':
    app = App()
    app.main()
