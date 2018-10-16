
![MP3 Voice Stamp Logo](img/banner.png)

## Usage ##

 * [Examples](#examples)
 * [Dry-run mode](#dry-run-mode)
 * [Configuration files](#configuration-files)
 * [Formatting spoken messages](#formatting-spoken-messages)


## Examples ##

 The simplest use case:

    mp3voicestamp -i music.mp3

 which would produce file named `music (mp3voicestamp).mp3` with audio overlay added to it with track title
 and time stamps every 5 minutes. You can also provide own name for the result file using `--out` switch:
 
    mp3voicestamp -i music.mp3 -o music_with_voice.mp3

 You can process more than one file at once:
 
    mp3voicestamp -i file1.mp3 file2.mp3 file3.mp3

 When using multiple input files you can still use `--out` but in such case it must point to the folder not a file:
 
    mp3voicestamp -i file1.mp3 file2.mp3 file3.mp3 -o my_folder

 You can change certain parameters, incl. frequency of tick announcer, or i.e. boost (or decrease) volume of voice
 overlay (relative to auto calculated volume level), change template for spoken track title or time announcements.
 and so on. 
  
 Sample MP3 included with this project was created with the following settings:
 
    mp3voicestamp --in music.mp3 --tick-offset 1 --tick-interval 1 --speech-volume 2

 All available options can be shown at any time using `--help` (or `-h`):
 
    mp3voicestamp --help

## Dry-run mode ##

 There's dry-run mode implemented, which is extremely useful esp. when doing batch processing of multiple files.
 By adding `--dry-run` to your command line arguments, you tells it to process all the input files files as it
 should, but no voice, normalizing, mixing steps would be executed nor the result files will be written. So you 
 can see what would happen in regular mode, before starting:
 
    mp3voicestamp -i *.mp3 --dry-run

 would show you:
    
    Files to process: 2
    Title format: "{title}"
    Tick format: "{minutes} minutes"
    Ticks interval 5 mins, start offset: 5 mins

    Processing "Momentum 49.mp3"
      Duration: 143 mins, tick count: 28
      Voice title: "Momentum 49"
      Output file "Momentum 49 (mp3voicestamp).mp3" *** FILE ALREADY EXISTS ***

    Processing "Clay van Dijk guest mix.mp3"
      Duration: 61 mins, tick count: 12
      Voice title: "Clay van Dijk guest mix"
      Output file "Clay van Dijk guest mix (mp3voicestamp).mp3" 
 

## Configuration files ##

 `Mp3VoiceStamp` supports configuration files aka profiles. Each file can configures all or some runtime parameters,
 then instead of using command line switches to tune up the tool, you tell it to read your config file.
 
 Said configuration file is plain text file following [INI file format](https://en.wikipedia.org/wiki/INI_file):
 
    [mp3voicestamp]
    file_out_format = "{name} (mp3voicestamp).{ext}"

    speech_speed = 150
    speech_volume_factor = 1.0

    title_format = "{title}"

    tick_add = 0
    tick_format = "{minutes} minutes"
    tick_offset = 5
    tick_interval = 5

 All entries are optional, and you can just put only those settings you want to be custom, using defaults for
 all the others:

    [mp3voicestamp]
    tick_format = "{minutes} long minutes passed"

 To use config file, just point to int with `--config` (or `-c`):
 
    mp3voicestamp -i music.mp3 -c my-settings.ini

 Note that command line arguments always shadow config file parameters. For example, if you save the following 
 config file as your `config.ini`:
 
    [mp3voicestamp]
    tick_format = "{minutes} minutes"
    tick_offset = 5
    tick_interval = 5

 and then invoke tool like this:
 
    mp3voicestamp -i music.mp3 -c config.ini --tick-offset 10

 then `tick offset` will be set to `10`.
 
 Finally keep in mind that `[mp3voicestamp]` is a section header and that thing **must always** be present in the file,
 otherwise it won't be read. If you need to keeps some notes in your config file, use of `#` at beginning of 
 the line to mark it as comment. See [example config file](../config/example.ini).
 
    [mp3voicestamp]

    # I want it to speak faster 
    speech_speed = 200

 
 ### Saving configuration files ###
 
 Instead of creating config file manually, you can use `--config-save` (`-cs`) option to dump current configuration
 state of the app to a file:
 
    mp3voicestamp -cs new-config.ini
   
 More over you can combine saving with config loading and manual tweaks as well:
 
    mp3voicestamp -c old-config.ini --tick-offset 10 --tick-format "{minutes} passed" -cs new-config.ini

 Which would load `old-config.ini` file, apply `tick-offset` and `tick-template` from your command line arguments
 and save it all to `new-config.ini` file which you can then tweak additionally or reuse as-is using `--config` option.
 
## Formatting spoken messages ##

 You can specify what should be said on your voice overlay for track announcement and time ticks. Dedicated options
 allow you to both used plain text but also, obviously, provide bunch of placeholders that are replaced prior
 speaking with the final value. Each placeholder uses `{key}` format and is then substituted by either
 the correct value, or if no value can be obtained (i.e. MP3 tags are not available) by empty string.
 You can combine multiple placeholders as well as enter regular text.
 
 ### Track title ###

 Default track title format string is `{title} {config_name}`. 
 
 | Key            | Description                                                                      |
 | -------------- | -------------------------------------------------------------------------------- |
 | {title}        | Track title from MP3 tags or based on file name if no tag is set                 |
 | {track_number} | Track number as set in tags or empty string                                      |
 | {artist}       | Artist name (if set) or album artist, otherwise empty string                     |
 | {album_artist} | Album artist or empty string                                                     |
 | {album_title}  | Album title or empty string                                                      |
 | {composer}     | Track composer or empty string                                                   |
 | {comment}      | Content of track comment field or empty string                                   |
 | {config_name}  | Name of loaded config file as specified with `config_name` key or empty string   |
 | {file_name}    | Name of the audio file without name extension                                    |

 > ![Tip](img/tip-small.png) If you don't want to have track title announced, set title format to empty 
 > string either in config or via command line argument `--title-format ""` 
 
 ### Ticks ###

 Default tick title format string is `{minutes} minutes`.

 | Key              | Description                                                                   |
 | ---------------- | ----------------------------------------------------------------------------- |
 | {minutes}        | Minutes since start of the track                                              | 
 | {minutes_digits} | Minutes but spoken as separate digits (i.e. "32" will be said as "three two") | 
 
 If you want, you can also use any of the track title placeholders in tick format too!
 
 > ![Tip](img/tip-small.png) If you don't want to have ticks said, set tick format to empty 
 > string either in config or via command line argument `--tick-format ""`.
 