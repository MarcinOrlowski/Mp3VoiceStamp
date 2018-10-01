![MP3 Voice Stamp Logo](img/logo.png)

 Athletes' companion: add synthetized voice overlay with various info and on-going timer to your audio files

## Table of contents ##

 * [Sample MP3 file](#sample)
 * [Introduction](#introduction)
 * [Features](#features)
 * [Usage examples](#examples)
 * [Requirements](#requirements)
 * [Bugs reports and pull requests](#contributing)
 * [Credits and license](#legal)
 * [Changelog](CHANGES.md)


## Sample ##

 ![Sample MP3](img/music.png) One image tells more that thousands words, so [download sample result file](sample/mp3voicestamp-demo.mp3)
 (MP3 file, 6 MiB size) and hear for yourself what this tool does in practice. For demo purposes time stamps are 
 announced at one minute interval, starting at first minute of the track.

----

 ![OceanPlanet Cover](img/oceanplanet.jpg)
 And if you are interested in music, sample is based on Olga Misty's DJ mix "Ocean Planet 086 Part 2" which can be found on 
 [MixCloud](https://www.mixcloud.com/olgamisty/olga-misty-ocean-planet-086-part-2-aug-06-2018-on-proton-radio/) and
 [SoundCloud](https://soundcloud.com/olga_misty/olga-misty-ocean-planet-086-part-2-aug-06-2018-on-proton-radio).


## Introduction ##
 
 Whenever you any physical activities, there's high chance you bring your music with you. So do I, but I do swim 
 a lot and in my case, my audio player UI is pretty non existent. I have just 5 control buttons and that's it.
 I cannot even tell what track I am currently listen to, unless I can recognize it. But as I swim, I personally
 prefer to run with so-called DJ mixes - 1 hour long (or more) mixed tracks of various artists. And as my swimming
 audio player offers no UI I faced two problems:
 
 * I sometimes had no clue what the mix I am starting to listen to
 * I often had problems telling how long I am swimming already
 
 So I wrote a tool to address these issues. The idea behind is quite simple: you take MP3 track of your choice
 and add synthetized voice overlay with required information. The voice tells what track title is (at its beginning)
 and then keeps speaking time passed at given intervals (each 5 minutes by default).


## Features ##

 * Reading MP3 tags
 * Automatic voice volume adjustment based on music file volume
 * Preserves bitrate of original audio file
 * Pretty customizable
 * Minimal runtime dependencies
 * Free


## Examples ##
 
 The simplest use case is like this:

    ./mp3voicestamp -i music.mp3

 which would produce file named `music (voicestamped).mp3` with audio overlay added to it with track title
 and time stamps every 5 minute.  
 
 Sample MP3 downloadable from[Sample](#sample) section was created with following settings:
 
    ./mp3voicestamp -i music.mp3 -tick-offset 1 -tick-interval 1 -tick-volume-factor 2

 See all available options with `-h`:
 
    ./mp3voicestamp -h   
 

## Requirements ##

 * [Python](https://www.python.org/) v2.7 or newer
 * required libraries:
   * [mutagen](https://github.com/quodlibet/mutagen/)
 * required tools:
   * [ffmpeg](https://www.ffmpeg.org/)
   * [normalize-audio](http://normalize.nongnu.org/)
   * [espeak](http://espeak.sourceforge.net/)
   * [sox](http://sox.sourceforge.net/)


 To install required Python libraries use `pip`:

    pip install mutagen

 To install required binaries (on Debian/Ubuntu):

    sudo apt install ffmpeg espeak normalize-audio sox


## Contributing ##

 Please report any issue spotted using [GitHub's project tracker](https://github.com/MarcinOrlowski/mp3voicestamp/issues).

 If you'd like to contribute to the this project, please [open new ticket](https://github.com/MarcinOrlowski/mp3voicestamp/issues)
 **before doing any work**. This will help us save your time in case I'd not be accept PR either completely or in proposed form.
 But if all is good and clear then follow common routine:

 * fork the project,
 * create new branch,
 * do your changes,
 * send pull request,
 * glory.
 

## Legal ##

 * Written and copyrighted &copy;2018 by Marcin Orlowski <mail (#) marcinorlowski (.) com>
 * MP3AudioStamp is open-sourced software licensed under the [MIT license](http://opensource.org/licenses/MIT)
 * Icons used in logo taken from free [Icons8 Olympics Sports Icon Pack](https://icons8.com/free-icons/olympics_sports)

