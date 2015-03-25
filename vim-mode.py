# gedit3-vim-mode: Vim-style keyboard navigation plugin for gedit3.
# Copyright 2015 Nicholas Parkanyi, licensed under GPLv3 (see 'gpl.txt')
from gi.repository import GObject, Gedit

class VimMode(GObject.Object, Gedit.ViewActivatable):
  __gtype_name__ = "VimMode"

  view = GObject.property(type=Gedit.View)

  def __init__(self):
    GObject.Object.__init__(self)
    self.block = False

  def do_activate(self):
    self.id = self.view.connect("key-press-event", self.process_keystroke)

  def do_deactivate(self):
    self.view.disconnect(self.id)
    
  def do_update_state(self):
    pass
    
  def process_keystroke(self, widget, event):
    if event.keyval == 0xff1b:
      self.block = not self.block
    #  'i' insert mode
    elif event.keyval == 0x069 and self.block:
      self.block = False
      return True
    elif self.block:
      self.update_cursor_iterator()
      # 'j' cursor down
      if event.keyval == 0x06a:
        self.cursor_down()
      # 'k' cursor up
      elif event.keyval == 0x06b:
        self.cursor_up()
      # 'l' cursor right
      elif event.keyval == 0x06c:
        self.cursor_right()
      # 'h' cursor left
      elif event.keyval == 0x068:
        self.cursor_left()
      self.buf.place_cursor(self.it)

    return self.block

  def update_cursor_iterator(self):
    self.buf = self.view.get_buffer()
    self.it = self.buf.get_start_iter()
    self.it.set_offset(self.buf.props.cursor_position)
    
  def cursor_down(self):
    self.it.forward_line()
    self.view.scroll_to_iter(self.it, 0.0, False, 0.0, 1.0)
    
  def cursor_up(self):
    self.it.backward_line()
    self.view.scroll_to_iter(self.it, 0.0, False, 0.0, 0.0)
    
  def cursor_right(self):
    self.it.forward_char()
    
  def cursor_left(self):
    self.it.backward_char()

