gedit3-vim-mode
================

This plugin enhances gedit3 with basic Vim-style keyboard navigation. To install,
just copy vim-mode.py and vim-mode.plugin to ~/.local/share/gedit/plugins/ on Unices
or C:\Program Files\gedit\lib\gedit\plugins on Windows. This requires PyGObject. It
has been tested in gedit 3.8, 3.14, 3.16, 3.18, and 3.20.

Features
--------
* normal mode cursor navigation, deletion
* repeating motions
* 'J' and 'K' move up and down by 15 lines
* Ctrl-C exits insert mode (copies selection in other modes)
* visual mode: copy and paste with 'y' and 'p'

Todo
----
* macros

Copyright © 2015-2017, 2021 Nicholas Parkanyi and contributors (see CONTRIBUTORS.md).
Distributed under the terms of the GNU General Public License, version 3
(see 'gpl.txt').
