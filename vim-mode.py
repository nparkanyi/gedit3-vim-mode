# gedit3-vim-mode: Vim-style keyboard navigation plugin for gedit3.
# Copyright 2015 Nicholas Parkanyi, licensed under GPLv3 (see 'gpl.txt')
from gi.repository import GObject, Gedit

class VimMode(GObject.Object, Gedit.ViewActivatable):
  __gtype_name__ = "VimMode"

  view = GObject.property(type=Gedit.View)

  def __init__(self):
    GObject.Object.__init__(self)
    self.block = False

  def callback(self, widget, event):
    if event.keyval == 0xff1b:
      self.block = not self.block
    elif event.keyval == 0x020 and self.block:
      buf = self.view.get_buffer()
      print(buf.props.cursor_position)
      it = buf.get_start_iter()
      buf.place_cursor(it)
    #  'i' insert mode
    elif event.keyval == 0x069 and self.block:
      self.block = False
      return True
    elif self.block:
      buf = self.view.get_buffer()
      it = buf.get_start_iter()
      it.set_offset(buf.props.cursor_position)
      # 'j' cursor down
      if event.keyval == 0x06a:
        it.forward_line()
      # 'k' cursor up
      elif event.keyval == 0x06b:
        it.backward_line()
      # 'l' cursor right
      elif event.keyval == 0x06c:
        it.forward_char()
      # 'h' cursor left
      elif event.keyval == 0x068:
        it.backward_char()
      buf.place_cursor(it)

    return self.block

  def do_activate(self):
    self.id = self.view.connect("key-press-event", self.callback)

  def do_deactivate(self):
    self.view.disconnect(self.id)

  def do_update_state(self):
    pass
