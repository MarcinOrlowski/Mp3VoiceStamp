 
## Table of contents ##

 * [Requirements](#requirements)
 * Installation
   * [Windows](#windows)
   * [Linux](#linux)

## Requirements ##

 * [Python](https://www.python.org/) v2.7 or newer
 * external tools:
   * [ffmpeg](https://www.ffmpeg.org/)
   * [normalize](http://normalize.nongnu.org/)
   * [espeak](http://espeak.sourceforge.net/)
   * [sox](http://sox.sourceforge.net/)

## Installation ##

 Installation differs and depends on target platform you use. Below you can find information or links to 
 binaries for your platform.

### Windows ###

 Since v1.2.0, binary installer for Windows is also available for download on project's 
 [Releases](https://github.com/MarcinOrlowski/Mp3VoiceStamp/releases) page, courtesy of
 JRSoftware's [InnoSetup](http://www.jrsoftware.org/isinfo.php).
 
 Please note there still is no GUI for the tool, and you will need to face Command Line to use it, but fear not - 
 that's pretty much trivial and already [covered in details](USAGE.md) in usage examples.

#### Binaries bundled #### 
 
 The following binaries are bundled in Windows installer:
 
  * [espeak v1.48](https://sourceforge.net/projects/espeak/files/espeak/espeak-1.48/setup_espeak-1.48.04.exe/download),
  * [ffmpeg v20181007-0a41a8b-win64](https://ffmpeg.zeranoe.com/builds/win64/static/ffmpeg-20181007-0a41a8b-win64-static.zip) 
  (more on this build [here](https://www.lesliesikos.com/install-ffmpeg-under-windows/)),
  * [sox v14.4.2](https://sourceforge.net/projects/sox/files/sox/14.4.2/),
  * [normalize v0.7.7](http://savannah.nongnu.org/download/normalize/normalize-0.7.7-win32.zip).
  
### Linux ###

 On Linux you need to check out the project from the repository using `git`. Then go to project folder and install
 python dependencies using `pip` tool:
 
     pip install -r requirements.txt --user

 Binary tools needed should be installed using your distribution's package manager. For Debian/Ubuntu it'd be like:

    apt install ffmpeg espeak normalize-audio sox
