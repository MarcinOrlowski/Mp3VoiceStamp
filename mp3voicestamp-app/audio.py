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
from util import Util


class Audio(object):

    @staticmethod
    def calculate_rms_amplitude(wav_file):
        """Calls SOX to get the RMS amplitude of WAV file

        Args:
            :wav_file

        Returns:
            float
        """
        src_amplitude_cmd = ['sox', wav_file, '-n', 'stat']
        rc, _, err = Util.execute(src_amplitude_cmd)
        if rc != 0:
            raise RuntimeError('Failed to calculate RMS amplitude of "{}"'.format(wav_file))

        # let's check what "sox" figured out
        sox_results = {re.sub(' +', '_', err[i].split(':')[0].strip().lower()): err[i].split(':')[1].strip() for i
                       in range(0, len(err))}
        return float(sox_results['rms_amplitude'])

    @staticmethod
    def adjust_wav_amplitude(wav_file, rms_amplitude):
        """Calls normalize-audio to adjust amplitude of WAV file

        Args:
            :wav_file
            :rms_amplitude
        """
        voice_gain_cmd = ['normalize-audio', '-a', str(rms_amplitude), wav_file]
        if Util.execute_rc(voice_gain_cmd) != 0:
            raise RuntimeError('Failed to adjust voice overlay volume')

    @staticmethod
    def mix_wav_tracks(file_out, encoding_quality, wav_files):
        """Mixes given WAV tracks together

        Args:
            :file_out
            :encoding_quality LAME encoder quality parameter
            :wav_files list of WAV files to mix
        """
        merge_cmd = ['ffmpeg', '-y']
        _ = [merge_cmd.extend(['-i', wav]) for wav in wav_files]
        merge_cmd.extend([
            '-filter_complex', 'amerge',
            '-ac', '2',
            '-c:a', 'libmp3lame',
            '-q:a', str(encoding_quality),
            file_out])
        if Util.execute_rc(merge_cmd) != 0:
            raise RuntimeError('Failed to create final MP3 file')
