gedit3-vim-mode
================

This plugin enhances gedit with basic Vim-style keyboard navigation. This has been
tested to work on gedit 3.8 to 3.38.

Features
--------
* normal mode cursor navigation, deletion
* repeating motions
* `J` and `K` move up and down by 15 lines
* Ctrl-C exits insert mode (copies selection in other modes)
* visual mode: copy and paste with `y` and `p`
* go to line number with `<number>G` or `<number>gg`

Installation
------------
Copy vim-mode.py and vim-mode.plugin to `~/.local/share/gedit/plugins/` on Unices
or `C:\Program Files\gedit\lib\gedit\plugins` on Windows. This requires PyGObject.

Todo
----
* macros

Copyright and License
---------------------
Copyright © 2015-2017, 2021 Nicholas Parkanyi and contributors (see
`CONTRIBUTORS.md`). Distributed under the terms of the GNU General Public License,
version 3 (see `GPL.txt`).
