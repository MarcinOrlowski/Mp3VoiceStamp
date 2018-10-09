
![MP3 Voice Stamp Logo](img/banner.png)

## Changelog ##

@dev
----
 * Track annoucement is now shown while processig to let you easily spot the problems with i.e. ID3 tags

v1.2.0 (2018-10-09)
-------------------
 * Corrected config file examples
 * MP3 failure returns with non-zero RC when only one input file is provided
 * Improved track title generation from file name
 * Moved usage documentation to separate document
 * App is less talkative. `--verbose` is gone now.
 * Improved Python3 code compatibility
 * Added `--dry-run` mode
 * Added support for `{file_name}` placeholder in title format
 * Fixed speech preprocessing dropping some parts under certain conditions
 * Default speech volume factor is now set to `2`
 * Copies some ID3 tags from source audio file to voices-tamped MP3 one
 * Added `{track_number}` to title format placeholders
 * `{artist}` title format placeholder now can include album artist if track artist is not set
 * Fixed `{title}` being empty string and not original file name, when MP3 file has the tag but empty
 * Track title placeholders are now supported for tick format as well
 * Title or tick format strings can now be empty (useful if you do not want either of them)
 * Default title format is now `{title} {config_name}`
 * Uses temp file for MP3 encoding for safe abort even if that file is expected to overwrite existing one
 * `normalize` tools is now properly invoked on Windows
 * Supports file name globing (useful on Windows, with lame CMD)
 
v1.1.0 (2018-10-04)
-------------------
 * Added support for batch processing of multiple audio files
 * Added `--verbose` and muted most of the messages by default
 * Complete rewrite for better internal architecture
 * Speech speed is now configurable
 * Added `--out-format` to customize how auto-generated files are named
 * Added `--title-format` for customized track title announcement format
 * Added support for config files for easier batch processing
 * Changed command line option name 

v1.0.0 (2018-10-01)
-------------------
 * Initial release
