## Changelog ##

dev
---
 * Corrected config file examples
 * MP3 failure returns with non-zero RC when only one input file is provided
 * Improved track title generation from file name
 * Moved usage documentation to separate document
 * App is less talkative. `--verbose` is gone now.
 * Improved Python3 code compatibility
 * Added `--dry-run` mode
 * Added support for `{file_name}` placeholder in title format
 * Fixed speach preprocessing dropping some parts under certain conditions
 * Default speech volume factor is now set to `2`

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
