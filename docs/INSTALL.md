 
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

## Installation ##

 Installation differs and depends on target platform you use. Below you can find information or links to 
 binaries for your platform.

### Windows ###

  * [Python 2.7](https://www.python.org/downloads/release/python-2715/)
  * [ffmpeg](https://www.lesliesikos.com/install-ffmpeg-under-windows/)
  * [normalize-audio](http://normalize.nongnu.org/) in `Binary downloads' section
  * [espeak](http://espeak.sourceforge.net/download.html)
  * [sox](https://sourceforge.net/projects/sox/files/sox/14.4.2/)
  
  once you got all binaries installed you need to install Python dependecies:
  
    pip install -r requirements.txt

### Debian/Ubuntu ###

 To install required Python libraries use `pip`:

    pip install -r requirements.txt

 To install required binaries (on Debian/Ubuntu):

    sudo apt install ffmpeg espeak normalize-audio sox

