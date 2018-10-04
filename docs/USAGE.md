
## Table of contents ##

 * [Usage examples](#usage-examples)
 * [Configuration files](#configuration-files)
 * [Formatting spoken messages](#formatting-spoken-messages)


## Usage examples ##
 
 The simplest use case is like this:

    ./mp3voicestamp -i music.mp3

 which would produce file named `music (voicestamped).mp3` with audio overlay added to it with track title
 and time stamps every 5 minute. You can also provide own name for result file using `--out`:
 
    ./mp3voicestamp -i music.mp3 -o music_with_voice.mp3

 You can also process more than one file at once:
 
    ./mp3voicestamp -i file1.mp3 file2.mp3 file3.mp3

 When using multiple input files you can still use `--out` but in such case it must point to target folder
 (so you loose ability to manually specify target file name):
 
    ./mp3voicestamp -i file1.mp3 file2.mp3 file3.mp3 -o my_folder/

 You can change certain parameters, incl. frequency of tick announcer, or i.e. boost (or decrease) volume of voice
 overlay (relative to auto calculated volume level), change template for spoken track title or time announcements. 
  
 Sample MP3 include with project was created with:
 
    ./mp3voicestamp --in music.mp3 --tick-offset 1 --tick-interval 1 --speech-volume 2

 or in short notation
 
     ./mp3voicestamp -i music.mp3 -to 1 -ti 1 -sv 2
 
 See all available options with `--help` (or `-h`).
 
## Configuration files ##

 `Mp3VoiceStamp` supports configuration files, so you can easily create one with settings of your choice and
 then use your file instead of passing all custom values via command line switches. It can also save current
 configuration to a file so you can easily preserve your settings with no hassle.
 
 Configuration file is plain text file following [INI file format](https://en.wikipedia.org/wiki/INI_file):
 
    [mp3voicestamp]
    file_out_format = "{name} (voicestamped).{ext}"

    speech_speed = 150
    speech_volume_factor = 1.0

    title_format = "{title}"

    tick_format = "{minutes} minutes"
    tick_offset = 5
    tick_interval = 5

 All keys are optional, so you can put just these you want to be custom. All other values will then fall back
 to defaults:

    [mp3voicestamp]
    tick_format = "{minutes} long minutes passed"

 To use config file specify path to the file with `--config` (or `-c`):
 
    ./mp3voicestamp -i music.mp3 -c my-settings.ini

 Additionally, command line arguments overshadow config file parameters. For example if you save the following 
 config file as your `config.ini`:
 
    [mp3voicestamp]
    tick_format = "{minutes} minutes"
    tick_offset = 5
    tick_interval = 5

 and then invoke tool like this:
 
    ./mp3voicestamp -i music.mp3 -c config.ini --tick-offset 10

 then `tick offset` will be set to `10`, shadowing config file entry.
 
 Finally `[mp3voicestamp]` is a section header and must always be present in the file. You also add comments
 with use of `#` at beginning of comment line. See [example config file](../example-config.ini).
 
 ### Saving configuration files ###
 
 You can use `--config-save` (`-cs`) option to dump current configuration state to a file for further reuse:
 
    ./mp3voicestamp -cs new-config.ini
 
 More over you can combine saving with config loading and manual tweaks as well:
 
    ./mp3voicestamp -c old-config.ini --tick-offset 10 --tick-format "{minutes} passed" -cs new-config.ini

 Which would load `old-config.ini` file, apply `tick-offset` and `tick-template` from your command line arguments
 and save it all to `new-config.ini` file which you can then reuse as usuall using said `--config` option.
 
## Formatting spoken messages ##

 You can define how both track title and clock tickes should be spoken by using configuring the format, 
 using supported placeholders. Each placeholder uses `{name}` format and is then substituted by either
 the correct value, or if no value can be obtained (i.e. MP3 tags are not available) by empty string.
 You can combine multiple placeholders as well as enter regular text.
 
 ### Track title ###

 Default track title format string is `{title} {config_name}` 
 
 | Key            | Description                                                                      |
 | -------------- | -------------------------------------------------------------------------------- |
 | {title}        | Track title from MP3 tags or based on file name if no tag is available           |
 | {artist}       | Artist name or empty string                                                      |
 | {album_artist} | Album artist or empty string                                                     |
 | {album_title}  | Album title or empty string                                                      |
 | {composer}     | Track composer or empty string                                                   |
 | {comment}      | Content of track comment field or empty string                                   |
 | {config_name}  | Name of loaded config file (with `.ini` name extension stripped) or empty string |

 ### Ticks ###

 Default tick title format string is `{minutes} minutes`.

 | Key       | Description                      |
 | --------- | -------------------------------- |
 | {minutes} | Minutes since start of the track | 
