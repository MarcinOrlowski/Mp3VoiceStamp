# coding=utf8

"""

 MP3 Voice Stamp

 Athletes' companion: adds synthetized voice overlay with various
 info and on-going timer to your audio files

 Copyright ©2018 Marcin Orlowski <mail [@] MarcinOrlowski.com>

 https://github.com/MarcinOrlowski/Mp3VoiceStamp

"""

from __future__ import print_function

import re

from mp3voicestamp_app.util import Util
from mp3voicestamp_app.tools import Tools


class Audio(object):

    def __init__(self, tools):
        """Init

        :param Tools tools: Instance of Tools class
        """
        self.__tools = tools

    def calculate_rms_amplitude(self, wav_files_list):
        """Calls SOX to get the RMS amplitude of WAV file

        :param list wav_files_list:
        :return: float
        """
        src_amplitude_cmd = [self.__tools.get_tool(Tools.KEY_SOX)]
        src_amplitude_cmd.extend(wav_files_list)
        src_amplitude_cmd.extend(['-n', 'stat'])
        rc, _, err = Util.execute(src_amplitude_cmd)
        if rc != 0:
            raise RuntimeError('Failed to calculate RMS amplitude')

        # let's check what "sox" figured out
        sox_results = {re.sub(' +', '_', err[i].split(':')[0].strip().lower()): err[i].split(':')[1].strip() for i
                       in range(0, len(err))}
        return float(sox_results['rms_amplitude'])

    def adjust_wav_amplitude(self, wav_file, rms_amplitude):
        """Calls normalize tool to adjust amplitude of audio file

        :param str wav_file:
        :param float rms_amplitude:
        :raises RuntimeError
        """
        if rms_amplitude > 1.0:
            rms_amplitude = 1.0

        voice_gain_cmd = [self.__tools.get_tool(Tools.KEY_NORMALIZE), '-a', str(rms_amplitude), wav_file]
        if Util.execute_rc(voice_gain_cmd) != 0:
            raise RuntimeError('Failed to adjust amplitude of "{name}"'.format(name=wav_file))

    def mix_wav_tracks(self, result_file_name, encoding_quality, src_wav_files):
        """Calls normalize tool to adjust amplitude of audio file

        :param str result_file_name: result file name
        :param int encoding_quality: LAME encoder quality parameter
        :param list[str] src_wav_files: list of source WAV files to mix

        :raises RuntimeError
        """
        """Mixes given WAV tracks together

        Args:
            :file_out
            :encoding_quality 
            :wav_files list of WAV files to mix
        """
        merge_cmd = [self.__tools.get_tool(Tools.KEY_FFMPEG), '-y']
        _ = [merge_cmd.extend(['-i', file_name]) for file_name in src_wav_files]
        merge_cmd.extend([
            '-filter_complex', 'amix=inputs={cnt}:duration=longest:dropout_transition=0'.format(cnt=len(src_wav_files)),
            '-ac', '2',
            '-c:a', 'libmp3lame',
            '-q:a', str(encoding_quality),
            result_file_name])

        if Util.execute_rc(merge_cmd) != 0:
            raise RuntimeError('Failed to create final MP3 file')
