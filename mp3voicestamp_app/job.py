# coding=utf8

"""

 MP3 Voice Stamp

 Athletes' companion: adds synthetized voice overlay with various
 info and on-going timer to your audio files

 Copyright ©2018 Marcin Orlowski <mail [@] MarcinOrlowski.com>

 https://github.com/MarcinOrlowski/Mp3VoiceStamp

"""

from __future__ import print_function

import shutil
import tempfile
import wave

from mp3voicestamp_app.audio import Audio
from mp3voicestamp_app.config import *
from mp3voicestamp_app.log import Log
from mp3voicestamp_app.mp3_file_info import Mp3FileInfo
from mp3voicestamp_app.tools import Tools
from mp3voicestamp_app.util import Util


class Job(object):
    def __init__(self, config, tools):
        """

        :param Config config:
        :param Tools tools:
        """
        # ensure config params make sense
        config.validate()

        self.__config = config
        self.__tmp_dir = None
        self.__tmp_mp3_file = None
        self.__tools = tools
        self.__audio = Audio(tools)

    def get_save_full_path(self, music_track, segment_number=None, ext=None):
        """Builds out file name based on provided template and music_track data

        :param Mp3FileInfo music_track:
        :param int|None segment_number:
        :param str|None ext:

        :return:
        :rtype:str
        """
        segment_name = ''
        if segment_number is not None:
            # generate segment target file name
            segment_name = ' (segment {segment_number_zeros}) '.format(
                segment_number=segment_number,
                segment_number_zeros='%03d' % segment_number
            )

        out_base_name, out_base_ext = Util.split_file_name(music_track.file_name)

        formatted_file_name = self.__config.file_out_format.format(
            name=out_base_name,
            segment_name=segment_name,
            ext=out_base_ext if ext is None else ext
        )

        out_file_name = os.path.basename(music_track.file_name)
        if self.__config.file_out is None:
            out_file_name = os.path.join(os.path.dirname(music_track.file_name), formatted_file_name)
        else:
            if os.path.isfile(self.__config.file_out):
                out_file_name = self.__config.file_out
            else:
                if os.path.isdir(self.__config.file_out):
                    out_file_name = os.path.join(self.__config.file_out, formatted_file_name)

        return out_file_name

    def __make_temp_dir(self):
        self.__tmp_dir = tempfile.mkdtemp(prefix='{app}_'.format(app=APP_NAME))

        Log.d('Tmp dir: {name}'.format(name=self.__tmp_dir))

    def __cleanup(self):
        if not self.__config.no_cleanup:
            if self.__tmp_dir is not None and os.path.isdir(self.__tmp_dir):
                shutil.rmtree(self.__tmp_dir)
                self.__tmp_dir = None

            if self.__tmp_mp3_file is not None and os.path.isfile(self.__tmp_mp3_file):
                os.remove(self.__tmp_mp3_file)
        else:
            print('Temp folder "{name}" not cleared.'.format(name=self.__tmp_dir))

    def speak_to_wav(self, text, out_file_name):
        """

        :param str text:
        :param str out_file_name:

        :return:
        :rtype:bool
        """
        # noinspection PyProtectedMember
        text_tmp_file = os.path.join(self.__tmp_dir, next(tempfile._get_candidate_names()) + '.txt')
        with open(text_tmp_file, "wb+") as fh:
            fh.write(text)
            fh.close()

            rc = Util.execute_rc([
                self.__tools.get_tool(Tools.KEY_ESPEAK),
                '-s', str(self.__config.speech_speed),
                '-z',
                '-w', out_file_name,
                '-f', text_tmp_file,
            ])

            if rc == 0 and not self.__config.no_cleanup:
                os.remove(text_tmp_file)

            return rc == 0

    def __blend_wavs(self, speak_wav_file_name, title_wav_file_name, result_file_name):
        """Merges title_wav into speak_wav (does not concatenate streams, but merges title into speak one!).

        :param str speak_wav_file_name:
        :param str title_wav_file_name:
        :param str result_file_name:

        :raises RuntimeError
        """
        # ffmpeg -i input1.mp3 -i input2.mp3 -filter_complex amerge -ac 2 -c:a libmp3lame -q:a 4 output.mp3
        blend_cmd = [self.__tools.get_tool(Tools.KEY_FFMPEG), '-y',
                     '-i', speak_wav_file_name,
                     '-i', title_wav_file_name,
                     '-filter_complex', 'amerge', '-ac', str(2),
                     result_file_name
                     ]
        if Util.execute_rc(blend_cmd) != 0:
            raise RuntimeError('Failed to blend WAVs')

    def __create_ticks_wav(self, speak_segments, speech_wav_file_name):
        """

        :param list speak_segments:
        :param str speech_wav_file_name:

        :raises:RuntimeError
        """
        segment_file_names = []

        for idx, segment_text in enumerate(speak_segments):
            segment_file_name = os.path.join(self.__tmp_dir, '{idx}.wav'.format(idx=idx))
            segment_file_names.append(segment_file_name)
            if not self.speak_to_wav(segment_text, segment_file_name):
                raise RuntimeError('Failed to speak "{text}" into "{file_name}".'.format(text=segment_text,
                                                                                         file_name=segment_file_name))

        # we need to get the frequency of speech waveform generated by espeak to be able to tell
        # ffmpeg how to pad/clip the part properly
        wav = wave.open(os.path.join(self.__tmp_dir, '0.wav'), 'rb')
        speech_frame_rate = wav.getframerate()
        wav.close()

        # create silence.wav
        silence_file_name = 'silence.wav'
        silence_duration_secs = 1
        silence_cmd = [self.__tools.get_tool(Tools.KEY_FFMPEG), '-y',
                       '-f', 'lavfi', '-i', 'anullsrc=sample_rate={rate}'.format(rate=speech_frame_rate),
                       '-t', str(silence_duration_secs),
                       os.path.join(self.__tmp_dir, silence_file_name)
                       ]
        if Util.execute_rc(silence_cmd) != 0:
            raise RuntimeError('Failed to create {name}'.format(name=silence_file_name))

        # prepend silence to segment file names
        segment_file_names.insert(0, silence_file_name)

        # merge voice overlay segments into one file with needed padding
        concat_cmd = [self.__tools.get_tool(Tools.KEY_FFMPEG), '-y']
        filter_complex = ''
        filter_complex_concat = ';'
        separator = ''

        max_len_tick = speech_frame_rate * 60 * self.__config.tick_interval
        max_len_title = speech_frame_rate * 60 * self.__config.tick_offset
        # for idx, segment_file_name in enumerate(segment_file_names):
        for idx, segment_file_name in enumerate(segment_file_names):
            concat_cmd.extend(['-i', os.path.join(self.__tmp_dir, segment_file_name)])

            # samples = rate_per_second * seconds * tick_interval_in_minutes
            max_len = max_len_title if idx == 0 else max_len_tick
            # http://ffmpeg.org/ffmpeg-filters.html#Filtergraph-description
            filter_complex += '{sep}[{idx}]apad=whole_len={len}[g{idx}]'.format(sep=separator, idx=idx, len=max_len)
            separator = ';'

            filter_complex_concat += '[g{idx}]'.format(idx=idx)

        filter_complex_concat += 'concat=n={len}:v=0:a=1'.format(len=len(segment_file_names))

        concat_cmd.extend(['-filter_complex', filter_complex + filter_complex_concat])
        concat_cmd.append(speech_wav_file_name)

        if Util.execute_rc(concat_cmd) != 0:
            raise RuntimeError('Failed to merge voice segments')

        # cleanup
        for idx, _ in enumerate(speak_segments):
            os.unlink(os.path.join(self.__tmp_dir, '{idx}.wav'.format(idx=idx)))

    def voice_stamp(self, mp3_file_name):
        """

        :param str mp3_file_name:
        :return:
        :rtype:bool
        """
        result = True

        try:
            # get some basic info about music track
            Log.level_push('Processing "{name}"'.format(name=mp3_file_name))
            music_track = Mp3FileInfo(mp3_file_name, self.__tools)

            if self.__config.verbose:
                Log.level_push('Track details')
                Log.v('Duration: {duration} secs'.format(duration=music_track.duration))
                Log.level_pop()

            # let's see if we need to split the audio track into smaller segments
            segments_count = 1
            track_segment_duration = music_track.duration
            if self.__config.split_segment_duration > 0:
                # we do, so we need to adjust certain checks too
                segments_count = int(
                    ((float(music_track.duration) / float(self.__config.split_segment_duration)) + 0.5))
                track_segment_duration = self.__config.split_segment_duration

            # some sanity checks first
            min_track_length = 1 + self.__config.tick_offset
            if track_segment_duration < min_track_length:
                raise ValueError(
                    'Track segment too short (min. {min}, current len {len})'.format(min=min_track_length,
                                                                                     len=track_segment_duration))

            if not self.__config.dry_run_mode:
                # create temporary folder
                self.__make_temp_dir()

                # convert source music track to WAV, splitting into segments if needed
                name, _ = Util.split_file_name(os.path.basename(music_track.file_name))
                music_wav_full_path = os.path.join(self.__tmp_dir, name + '.wav')

                dir_name = os.path.dirname(music_wav_full_path)
                name, ext = Util.split_file_name(music_wav_full_path)
                segment_file_name_pattern = os.path.join(dir_name, name + '.%03d.' + ext)

                music_track.to_wav_segments(segment_file_name_pattern, self.__config.split_segment_duration)

                # calculate RMS amplitude of music track as reference to gain voice to match
                audio_wav_segments_file_names = []
                for idx in range(0, segments_count):
                    audio_wav_segments_file_names.append(segment_file_name_pattern % idx)

                rms_amplitude = self.__audio.calculate_rms_amplitude(audio_wav_segments_file_names)
                target_speech_rms_amplitude = rms_amplitude * self.__config.speech_volume_factor
            else:
                target_speech_rms_amplitude = 25

            # --------------------------------------------------------------------------------------------

            # let's now create ticks.wav with our spoken ticks.
            ticks_per_segment = range(self.__config.tick_offset, track_segment_duration, self.__config.tick_interval)

            segments = []
            # if user sets tick format to empty string, we'd skip generating ticks completely
            if self.__config.tick_format != '':
                for time_marker in ticks_per_segment:
                    minutes = str(time_marker + self.__config.tick_add)
                    extras = {'minutes': minutes,
                              'minutes_digits': Util.separate_chars(minutes),
                              }
                    tick_string = Util.process_placeholders(self.__config.tick_format,
                                                            Util.merge_dicts(music_track.get_placeholders(), extras))
                    segments.append(Util.prepare_for_speak(tick_string))

            if self.__config.dry_run_mode:
                Log.i('Segment duration {len} minutes, {cnt} ticks per segment'.format(len=track_segment_duration,
                                                                                       cnt=(len(segments) - 1)))
                Log.v('Tick format "{format}"'.format(format=self.__config.tick_format))

            ticks_wav_full_path = os.path.join(self.__tmp_dir, 'ticks.wav')
            if not self.__config.dry_run_mode:
                self.__create_ticks_wav(segments, ticks_wav_full_path)

                # now adjust the amplitude of ticks wave
                self.__audio.adjust_wav_amplitude(ticks_wav_full_path, target_speech_rms_amplitude)

            # --------------------------------------------------------------------------------------------

            # let's process all the segments

            track_segment_name_format = 'segment {segment_number}'

            for segment_number in range(0, segments_count):
                segment_wav_file_name = self.get_save_full_path(music_track,
                                                                (segment_number + 1) if segments_count > 1 else None)

                Log.d('Doing segment {idx} as {file_name}'.format(
                    idx=segment_number, file_name=segment_wav_file_name))

                # # check if we can create output file too
                if not self.__config.dry_run_mode:
                    if os.path.exists(segment_wav_file_name) and not self.__config.force_overwrite:
                        raise OSError('Target "{name}" already exists. Use -f to force overwrite.'.format(
                            name=segment_wav_file_name))

                # NOTE: we will generate title WAV even if i.e. title_format is empty. This is intentional, to keep
                #       further logic simpler, because if both title and tick formats would be empty, then skipping
                #       WAV generation would left us with no speech overlay file for processing and mixing.
                #       I do not want to have the checks for such case

                # let's now create WAVs with our segment title part.
                extras = {
                    'config_name': self.__config.name,
                    'segment_number': '' if self.__config.split_segment_duration == 0 else (segment_number + 1),
                    'segment_count': segments_count,
                }

                __segment_name = ''
                if segments_count > 1:
                    __segment_name = Util.process_placeholders(track_segment_name_format, extras)
                extras['segment_name'] = __segment_name

                track_title_to_speak = Util.prepare_for_speak(
                    Util.process_placeholders(self.__config.title_format,
                                              Util.merge_dicts(music_track.get_placeholders(), extras)))
                Log.i('Announced as "{title}"'.format(title=track_title_to_speak))
                Log.v('Announcement format "{fmt}"'.format(fmt=self.__config.title_format))

                # ----------------------------------------------------------------------------------------

                # speak segment title
                segment_title_wav_full_path = os.path.join(self.__tmp_dir, 'title.wav')
                if not self.speak_to_wav(track_title_to_speak, segment_title_wav_full_path):
                    raise RuntimeError('Failed to speak track title')

                if not self.__config.dry_run_mode:
                    # now adjust the amplitude of title announcement wave
                    self.__audio.adjust_wav_amplitude(segment_title_wav_full_path, target_speech_rms_amplitude)

                    # mix all the streams together
                    Log.i('Writing: "{name}"'.format(name=segment_wav_file_name))

                    # noinspection PyProtectedMember
                    self.__tmp_mp3_file = os.path.join(os.path.dirname(segment_wav_file_name),
                                                       next(tempfile._get_candidate_names()) + '.mp3')

                    name, _ = Util.split_file_name(os.path.basename(music_track.file_name))
                    music_segment_wav_full_path = os.path.join(self.__tmp_dir, name + '.%03d.wav' % segment_number)

                    # noinspection PyUnboundLocalVariable
                    self.__audio.mix_wav_tracks(self.__tmp_mp3_file, music_track.get_encoding_quality_for_lame(), [
                        music_segment_wav_full_path,
                        segment_title_wav_full_path,
                        ticks_wav_full_path
                    ])

                    # copy some ID tags to newly create MP3 file
                    music_track.write_id3_tags(self.__tmp_mp3_file, track_title_to_speak)

                    if os.path.exists(segment_wav_file_name):
                        os.remove(segment_wav_file_name)

                    os.rename(self.__tmp_mp3_file, segment_wav_file_name)
                    self.__tmp_mp3_file = None
                else:
                    output_file_msg = 'Output file "{name}"'.format(name=segment_wav_file_name)
                    if os.path.exists(segment_wav_file_name):
                        output_file_msg += ' *** TARGET FILE ALREADY EXISTS ***'
                    Log.i(output_file_msg)
                    Log.v('Output file name format "{fmt}"'.format(fmt=self.__config.file_out_format))
                    Log.i('')

        except RuntimeError as ex:
            if not self.__config.debug:
                Log.e(ex)
            else:
                raise
            result = False

        finally:
            Log.level_pop()
            self.__cleanup()

        return result
