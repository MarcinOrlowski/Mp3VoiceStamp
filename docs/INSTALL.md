 
## Table of contents ##

 * [Requirements](#requirements)
 * Installation
   * [Windows](#windows)
   * [Debian/Ubuntu](#debianubuntu)


## Requirements ##

 * [Python](https://www.python.org/) v2.7 or newer
 * required libraries:
   * [mutagen](https://github.com/quodlibet/mutagen/)
 * required tools:
   * [ffmpeg](https://www.ffmpeg.org/)
   * [normalize-audio](http://normalize.nongnu.org/)
   * [espeak](http://espeak.sourceforge.net/)
   * [sox](http://sox.sourceforge.net/)
   * [lame](http://lame.sourceforge.net/)

## Installation ##

### Windows ###

  * [ffmpeg](https://www.lesliesikos.com/install-ffmpeg-under-windows/)
  * [normalize-audio](http://normalize.nongnu.org/) in `Binary downloads' section

### Debian/Ubuntu ###

 To install required Python libraries use `pip`:

    pip install -r requirements.txt

 To install required binaries (on Debian/Ubuntu):

    sudo apt install ffmpeg espeak normalize-audio sox

