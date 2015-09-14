gedit3-vim-mode
================

This plugin enhances gedit3 with basic Vim-style keyboard navigation. To install,
just copy vim-mode.py and vim-mode.plugin to ~/.local/share/gedit/plugins/ . This
requires PyGObject. It has been tested in gedit 3.8, 3.14, and 3.16.

Features
--------
* normal mode cursor navigation, deletion
* repeating motions
* 'J' and 'K' move up and down by 15 lines
* Ctrl-C exits insert mode (copies selection in other modes)

Todo
----
* visual mode
* macros

Copyright 2015 Nicholas Parkanyi. Distributed under the terms of the GNU General Public
License, version 3 (see 'gpl.txt').
