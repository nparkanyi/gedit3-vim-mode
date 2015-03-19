from gi.repository import GObject, Gedit

class VimMode(GObject.Object, Gedit.ViewActivatable):
  __gtype_name__ = "VimMode"
  
  view = GObject.property(type=Gedit.View)
  
  def __init__(self):
    GObject.Object.__init__(self)
    self.block = False
    
  def callback(self, widget, event):
    if (event.keyval == 0xff1b):
      self.block = not self.block
    return self.block
    
  def do_activate(self):
    self.id = self.view.connect("key-press-event", self.callback)
    
  def do_deactivate(self):
    self.view.disconnect(self.id)
    
  def do_update_state(self):
    pass
