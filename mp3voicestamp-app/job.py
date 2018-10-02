# coding=utf8

"""

 MP3 Voice Tag

 Athletes' companion: add synthetized voice overlay with various
 info and on-going timer to your audio files

 Copyright ©2018 Marcin Orlowski <mail [@] MarcinOrlowski.Com>

 https://github.com/MarcinOrlowski/mp3voicestamp

"""

import os
import shutil
import tempfile


class Job(object):

    def __init__(self, args, file_in):
        self.args = args

        self.file_in = file_in

        self.tick_pattern = args.tick_pattern
        self.tick_offset = args.tick_offset
        self.tick_interval = args.tick_interval
        self.tick_volume_factor = args.tick_volume_factor

        self.title_pattern = args.title_pattern

        self.force = args.force

        out_base_name = os.path.basename(file_in)
        if out_base_name[-4:] == '.mp3':
            out_base_name = out_base_name[:-4]
        out_file_name = '{} (voicestamped).mp3'.format(out_base_name)
        self.file_out = out_file_name

        if args.file_out is None:
            self.file_out = os.path.join(os.path.dirname(file_in), out_file_name)
        else:
            if os.path.isfile(args.file_out):
                self.file_out = args.file_out
            else:
                if os.path.isdir(args.file_out):
                    self.file_out = os.path.join(args.file_out, out_file_name)

        self.tmp_dir = None

    def init(self):
        self.make_temp_dir()

    def make_temp_dir(self):
        self.tmp_dir = tempfile.mkdtemp()

    def cleanup(self):
        if self.tmp_dir is not None:
            shutil.rmtree(self.tmp_dir)
