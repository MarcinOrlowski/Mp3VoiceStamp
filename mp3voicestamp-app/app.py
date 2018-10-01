# coding=utf8

from __future__ import print_function

import os
import shutil
import signal
import tempfile
from collections import OrderedDict

from args import Args
from util import Util


# #################################################################
#
# MP3 Voice Tag
#
# Athletes' companion: add synthetized voice overlay with various
# info and on-going timer to your audio files
#
# #################################################################
#
# Copyright ©2018 Marcin Orlowski <mail [@] MarcinOrlowski.Com>
#
# Project page: https://github.com/MarcinOrlowski/mp3voicestamp
#
# #################################################################

class App(object):
    supported_keys = OrderedDict([
        ('title', 'TIT2'),
        ('artist', 'TPE1'),
        ('album_artist', 'TPE2'),
        ('composer', 'TCOM'),
        ('performer', 'TOPE'),
        ('album', 'TALB'),
        ('comment', 'COMM::XXX:'),
    ])

    def __init__(self):
        self.args = None
        self.tmp_dir = None

    def sigint_handler(self, unused_signal, unused_frame):
        self.cleanup()

    def cleanup(self):
        if self.args.no_cleanup and self.tmp_dir is not None:
            shutil.rmtree(self.tmp_dir)

    def get_mp3_info(self, mp3_file_name):
        from mutagen.mp3 import MP3

        mp3 = MP3(mp3_file_name)

        # get track title either from tag, or from filename
        tag_title = 'TIT2'

        info = OrderedDict([
            ('file_name', mp3_file_name),
            ('duration', int(round(mp3.info.length / 60 + 0.5))),
            ('bitrate', mp3.info.bitrate),
        ])

        for key, tag in self.supported_keys.items():
            if key == 'TIT2':
                val = str(mp3_file_name[:-4].replace('_', ' ') if tag_title not in mp3 else mp3[tag_title])
            else:
                val = '' if tag not in mp3 else mp3[tag]
            info[key] = val

        return info

    def guess_encoding_quality_for_lame_encoder(self, bitrate):
        # based on https://trac.ffmpeg.org/wiki/Encode/MP3
        quality = 0
        for avg in [245, 225, 190, 175, 165, 130, 115, 100, 85, 65]:
            if bitrate >= avg * 1000:
                break
            else:
                quality += 1

        return quality

    def check_env(self):
        tools = ['ffmpeg', 'normalize-audio', 'espeak', 'sox']
        for tool in tools:
            if Util.which(tool) is None:
                Util.abort('Missing "{}". See README.md for list of mandatory dependencies.'.format(tool))

    def speak_to_wav(self, text, out_file_name):
        rc = Util.execute_rc(['espeak', '-s', '150', '-z', '-w', out_file_name, str(text)])
        return rc == 0

    def main(self):
        import wave

        self.check_env()

        # parse comman line arguments
        self.args = Args.parse_args()
        Util.init(self.args)

        # ensure it's safe to write use give name for output file
        if os.path.exists(self.args.file_out):
            if not self.args.force:
                Util.abort('Target "{}" already exists'.format(self.args.file_out))
            if not os.path.isfile(self.args.file_out):
                Util.abort('Target "{}" is not a file. Cannot overwrite'.format(self.args.file_out))

        # get some info about source MP3 file and print it
        in_file_info = self.get_mp3_info(self.args.file_in)
        Util.print_info(in_file_info, 'Input track info')

        # some sanity checks.
        min_track_length = 1 + self.args.tick_offset
        if in_file_info['duration'] < min_track_length:
            Util.abort('Input MP3 track must be at least {} minutes long'.format(min_track_length))

        # create temp folder where all out working files will live for a while
        self.tmp_dir = tempfile.mkdtemp()
        Util.debug('Temporary folder: {}'.format(self.tmp_dir))

        # plant SIGINT handler, so we can clean up temp folder when interrupted
        signal.signal(signal.SIGINT, self.sigint_handler)

        # prepare some placeholders to be later use for speaking track title.
        track_title = self.args.title_pattern.format(
            title=in_file_info['title'],
            artist=in_file_info['artist'],
            album_artist=in_file_info['album_artist'],
            composer=in_file_info['composer'],
            performer=in_file_info['performer'],
            album=in_file_info['album'],
            comment=in_file_info['comment']
        )

        # let's see how many time stamps we are going to have
        ticks = range(self.args.tick_offset,
                      in_file_info['duration'],
                      self.args.tick_interval)
        out_file_info = OrderedDict([
            ('file_name', self.args.file_out),
            ('quality', self.guess_encoding_quality_for_lame_encoder(in_file_info['bitrate'])),
            ('title_pattern', self.args.title_pattern),
            ('title_overlay', track_title),
            ('tick_pattern', self.args.tick_pattern),
            ('tick_offset', self.args.tick_offset),
            ('tick_interval', self.args.tick_interval),
            ('tick_volume_factor', self.args.tick_volume_factor),
            ('tick_count', len(ticks))
        ])
        # print some info about what we are going to produce and how
        Util.print_info(out_file_info, 'Output track info')

        # let's now create WAVs with our spoken parts. First goes track title, then time stamps
        segments = [track_title]
        Util.print_no_lf('Creating spoken overlays')
        for time_marker in ticks:
            segments.append(out_file_info['tick_pattern'].format(time_marker))

        for idx, segment_text in enumerate(segments):
            segment_file_name = os.path.join(self.tmp_dir, '{}.wav'.format(idx))
            if not self.speak_to_wav(segment_text, segment_file_name):
                Util.abort('Failed to create "{0}" as "{1}".'.format(segment_text, segment_file_name))
        Util.print('OK')

        # we need to get the frequency of speech waveform generated by espeak to later be able to tell
        # ffmpeg how to pad/clip the part
        wav = wave.open(os.path.join(self.tmp_dir, '0.wav'), 'rb')
        speech_meged_wav_full = os.path.join(self.tmp_dir, 'speech.wav')
        speech_frame_rate = wav.getframerate()
        wav.close()

        # merge voice overlay segments into one file with needed padding
        Util.print_no_lf('Merging voice overlays')
        concat_cmd = ['ffmpeg', '-y']
        filter_complex = ''
        filter_complex_concat = ';'
        separator = ''

        max_len_tick = speech_frame_rate * 60 * out_file_info['tick_interval']
        max_len_title = speech_frame_rate * 60 * out_file_info['tick_offset']
        for idx, i in enumerate(segments):
            concat_cmd.extend(['-i', os.path.join(self.tmp_dir, '{}.wav'.format(idx))])

            # samples = rate_per_second * seconds * tick_interval_in_minutes
            max_len = max_len_title if idx == 0 else max_len_tick
            # http://ffmpeg.org/ffmpeg-filters.html#Filtergraph-description
            filter_complex += '{}[{}]apad=whole_len={}[g{}]'.format(separator, idx, max_len, idx)
            separator = ';'

            filter_complex_concat += '[g{}]'.format(idx)

        filter_complex_concat += 'concat=n={}:v=0:a=1'.format(len(segments))

        concat_cmd.extend(['-filter_complex', filter_complex + filter_complex_concat])
        concat_cmd.append(speech_meged_wav_full)

        if Util.execute_rc(concat_cmd) != 0:
            Util.abort('Failed to merge voice segments')
        Util.print('OK')

        # convert source mp3 to wav
        # this is needed for many reasons:
        # we need to adjust voice overlay amplitude to match MP3 file level and to do that we use "sox" too
        # which cannot deal with MP3 directly.
        # Also there are some odd issues with "ffmpeg" failing during merge when source was in mp3 - blid guess for now
        # it was due to some struct mismatch between MP3 file (i.e. having cover image), and speech segments being
        # just waveform. Most likely this can be solved better way but we need WAV anyway so no point wasting time
        # at the moment.

        source_wav_file_name = self.args.file_in + '.wav'
        source_wav_full_path = os.path.join(self.tmp_dir, source_wav_file_name)
        Util.print_no_lf('Creating temporary WAV')
        wav_cmd = ['ffmpeg', '-i', self.args.file_in, source_wav_full_path]
        if Util.execute_rc(wav_cmd) != 0:
            Util.abort('Failed to convert to WAV file')
        Util.print('OK')

        # now let's get the RMS amplitude of our track
        Util.print_no_lf('Calculating RMS amplitude')
        src_amplitude_cmd = ['sox', source_wav_full_path, '-n', 'stat']
        rc, output, err = Util.execute(src_amplitude_cmd)
        if rc != 0:
            Util.abort('Failed to calculated RMS amplitude')

        # let's check what "sox" figured out
        import re
        src_sox_results = {re.sub(' +', '_', err[i].split(':')[0].strip().lower()): err[i].split(':')[1].strip() for i
                           in range(0, len(err))}
        file_in_rms_amplitude = float(src_sox_results['rms_amplitude'])
        Util.print(file_in_rms_amplitude)

        voice_volume_adjustment = file_in_rms_amplitude * out_file_info['tick_volume_factor']
        Util.print('Voice overlay target amplitude: {}'.format(voice_volume_adjustment))

        Util.print_no_lf('Adjusting volume of voice overlay')
        voice_gain_cmd = ['normalize-audio', '-a', str(voice_volume_adjustment), speech_meged_wav_full]
        if Util.execute_rc(voice_gain_cmd):
            Util.abort('Failed to adjust voice overlay volume')
        Util.print('OK')

        Util.print_no_lf('Creating output MP3 file')
        merge_cmd = ['ffmpeg', '-y',
                     '-i', os.path.join(self.tmp_dir, source_wav_file_name),
                     '-i', os.path.join(self.tmp_dir, 'speech.wav'),
                     '-filter_complex', 'amerge', '-ac', '2', '-c:a', 'libmp3lame',
                     '-q:a', '{}'.format(out_file_info['quality']),
                     self.args.file_out]
        if Util.execute_rc(merge_cmd) != 0:
            Util.abort('Failed to create final MP3 file')
        Util.print('OK')

        # cleanup
        if not self.args.no_cleanup:
            self.cleanup()
        else:
            if self.args.debug:
                Util.debug('Leaving "{}" folder intact'.format(self.tmp_dir))


# ---------------------------------------------------------------------------------

if __name__ == '__main__':
    app = App()
    app.main()
