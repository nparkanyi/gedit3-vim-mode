# -*- coding: utf-8 -*-
# gedit3-vim-mode: Vim-style keyboard navigation plugin for gedit3.
# Copyright © 2015-2017, 2021 Nicholas Parkanyi and contributors (see CONTRIBUTORS.md)
# Licensed under GPLv3 (see gpl.txt)
from gi.repository import GObject, Gedit, Gdk, Gtk


mode_text = 'Vim Mode: NORMAL'


class VimModeWindow(GObject.Object, Gedit.WindowActivatable):
    __gtype_name__ = "VimModeWindow"

    window = GObject.property(type=Gedit.Window)

    def __init__(self):
        GObject.Object.__init__(self)

    def do_activate(self):
        global mode_text
        self.status_bar = self.window.get_statusbar()
        self.ctx_id = self.status_bar.get_context_id('vim_mode')
        self.id = self.window.connect('key-release-event', \
				      self.update_statusbar)
        self.status_bar.push(self.ctx_id, mode_text)

    def do_update_state(self):
        pass

    def update_statusbar(self, widget, event):
        global mode_text
        self.status_bar.pop(self.ctx_id)
        self.status_bar.push(self.ctx_id, mode_text)
        return False


class VimMode(GObject.Object, Gedit.ViewActivatable):
    __gtype_name__ = "VimMode"

    view = GObject.property(type=Gedit.View)

    def __init__(self):
        GObject.Object.__init__(self)
        self.argument_digits = []
        # when first 'g' is pressed, remember argument number for second 'g'
        # 0 means no argument number explicitly given
        self.gg_argument = 0
        self.g_pressed = False
        self.d_pressed = False
        self.is_visual_mode = False
        self.block = True
        #True if Control is held
        self.modifiers = False

    def do_activate(self):
        self.id_press = self.view.connect("key-press-event", \
					  self.process_keystroke)
        self.id_release = self.view.connect("key-release-event", \
					    self.process_keyrelease)

        self.update_cursor_iterator()
        self.line_offset = self.it.get_line_offset()
        self.clip = Gtk.Clipboard.get(Gdk.Atom.intern('CLIPBOARD', True))

    def do_deactivate(self):
        self.view.disconnect(self.id_press)
        self.view.disconnect(self.id_release)

    def do_update_state(self):
        pass

    def process_keyrelease(self, widget, event):
        if event.keyval == Gdk.keyval_from_name('Control_L')\
                or event.keyval == Gdk.keyval_from_name('Control_R'):
            self.modifiers = False

        return False

    def process_keystroke(self, widget, event):
        if event.keyval != Gdk.keyval_from_name('g'):
            self.g_pressed = False

        if event.keyval == Gdk.keyval_from_name('Escape'):
            self.normal_mode()
            # cancel delete motions
            self.d_pressed = False
            return True
        # Ctrl-C enters normal mode, only when in insert mode
        if event.keyval == Gdk.keyval_from_name('c') \
                and event.state & Gdk.ModifierType.CONTROL_MASK != 0 \
                and (not self.block or self.is_visual_mode):
            self.normal_mode()
            return True

        # 'Ctrl-R' primitive redo
        # (just the same as ctrl+shift+z, not the vim redo)
        if event.keyval == Gdk.keyval_from_name('r') \
           and event.state & Gdk.ModifierType.CONTROL_MASK != 0:
            if self.buf.can_redo():
                self.buf.redo()
            return True

        # ignore arrow keys
        elif Gdk.keyval_from_name('Left') <= event.keyval \
					  <= Gdk.keyval_from_name('Down'):
            return False
        # ignore shift keypress event
        elif event.keyval == Gdk.keyval_from_name('Shift_L') \
                or event.keyval == Gdk.keyval_from_name('Shift_R'):
            return False
        # ignore control
        elif event.keyval == Gdk.keyval_from_name('Control_L') \
                or event.keyval == Gdk.keyval_from_name('Control_R'):
            self.modifiers = True
            return False

        elif self.block and not self.modifiers:
            # 'i' insert mode
            if event.keyval == Gdk.keyval_from_name('i'):
                self.insert_mode()
                return True
            elif event.keyval == Gdk.keyval_from_name('v'):
                if self.is_visual_mode:
                    self.normal_mode()
                else:
                    self.visual_mode()
                return True
            # 'a' insert after cursor
            elif event.keyval == Gdk.keyval_from_name('a'):
                self.update_cursor_iterator()
                self.cursor_right()
                self.buf.place_cursor(self.it)
                self.insert_mode()
                return True
            # 'A' insert mode from end of line
            elif event.keyval == Gdk.keyval_from_name('A'):
                self.update_cursor_iterator()
                self.cursor_end_line()
                self.buf.place_cursor(self.it)
                self.insert_mode()
                return True
            elif event.keyval == Gdk.keyval_from_name('y'):
                if self.is_visual_mode:
                    self.buf.copy_clipboard(self.clip)
                self.normal_mode()
                return True
            # '1' to '9': argument digits
            elif Gdk.keyval_from_name('1') <= event.keyval \
					   <= Gdk.keyval_from_name('9'):
                self.add_argument_digit(event.keyval - Gdk.keyval_from_name('0'))
                return True
            # '0' as argument digit only if user has already entered other digits
            elif event.keyval == Gdk.keyval_from_name('0') \
			and len(self.argument_digits) > 0:
                self.add_argument_digit(0)
                return True

            self.update_cursor_iterator()

            # 'd' begin delete motion
            if event.keyval == Gdk.keyval_from_name('d') and not self.d_pressed:
                if self.is_visual_mode:
                    self.buf.delete(self.buf.get_iter_at_mark( \
					self.buf.get_mark('selection_bound')), \
                                    self.buf.get_iter_at_mark( \
					self.buf.get_mark('insert')))
                    self.normal_mode()
                    return True
                else:
                    self.d_pressed = True
                    return True
            # 'O' insert new line above
            elif event.keyval == Gdk.keyval_from_name('O'):
                indent = self.get_line_indent()
                self.cursor_insert_line_above()
                self.buf.place_cursor(self.it)
                self.buf.insert_at_cursor(indent, len(indent))
                return True
            # 'o' insert new line below
            elif event.keyval == Gdk.keyval_from_name('o'):
                indent = self.get_line_indent()
                self.cursor_insert_line_below()
                self.buf.insert_at_cursor(indent, len(indent))
                return True

            argument = 1
            if len(self.argument_digits) > 0:
                place = 1
                argument = 0
                for i in range(len(self.argument_digits), 0, -1):
                    argument += place * self.argument_digits[i-1]
                    place *= 10

            # 'x' delete char under cursor
            if event.keyval == Gdk.keyval_from_name('x') \
                    and not self.d_pressed:
                if self.is_visual_mode:
                    self.buf.delete(self.buf.get_iter_at_mark( \
					self.buf.get_mark('selection_bound')), \
                                    self.buf.get_iter_at_mark( \
					self.buf.get_mark('insert')))
                    self.normal_mode()
                    return True
                else:
                    for x in range(argument):
                        self.cursor_delete_char()
                    return True

            # 'p' paste from clipboard
            if event.keyval == Gdk.keyval_from_name('p') and not self.d_pressed:
                for x in range(argument):
                    self.buf.paste_clipboard(self.clip, None, True)
                return True

            # 'u' primitive undo
            # (just the same as ctrl+z, not the vim undo)
            if event.keyval == Gdk.keyval_from_name('u') and not self.d_pressed:
                if self.buf.can_undo():
                    self.buf.undo()
                return True

            # repeatable commands
            if self.d_pressed:
                # delete motions
                self.delete_from = self.buf.get_start_iter()
                self.delete_from.assign(self.it)

                if event.keyval == Gdk.keyval_from_name('g') \
                        and self.g_pressed:
                    self.cursor_start_buffer()
                    self.d_pressed = False
                elif event.keyval == Gdk.keyval_from_name('d'):
                    self.cursor_start_line()
                    self.delete_from.assign(self.it)
                    for x in range(argument - 1):
                        self.cursor_down()
                    self.cursor_end_line()
                    self.it.forward_char()
                else:
                    self.process_cursor_motions(event, argument)

                self.argument_digits = []
                self.buf.delete(self.delete_from, self.it)
                if event.keyval != Gdk.keyval_from_name('g') \
                        or not self.g_pressed:
                    self.d_pressed = False
            else:
                self.process_cursor_motions(event, argument)
                self.argument_digits = []
                if not self.is_visual_mode:
                    self.buf.place_cursor(self.it)
                else:
                    self.buf.create_mark('insert', self.it, False)

        if self.modifiers:
            return False
        else:
            return self.block

    def insert_mode(self):
        global mode_text
        self.block = False
        self.d_pressed = False
        self.is_visual_mode = False
        mode_text = 'Vim Mode: INSERT'

    def normal_mode(self):
        global mode_text
        self.block = True
        self.is_visual_mode = False
        self.update_cursor_iterator()
        self.buf.place_cursor(self.it)
        mode_text = 'Vim Mode: NORMAL'

    def visual_mode(self):
        global mode_text
        self.block = True
        self.is_visual_mode = True
        self.update_cursor_iterator()
        self.buf.create_mark('selection_bound', self.it, False)
        mode_text = 'Vim Mode: VISUAL'

    def process_cursor_motions(self, event, repeat):
        try:
            # 'gg'
            if event.keyval == Gdk.keyval_from_name('g'):
                # first 'g'
                if not self.g_pressed:
                    if len(self.argument_digits) > 0:
                        self.gg_argument = repeat
                    self.g_pressed = True
                    return
                # '<number>gg' cursor to that line number
                elif self.gg_argument > 0:
                    self.cursor_go_to_line(self.gg_argument)
                # 'gg' cursor to start of buffer
                else:
                    self.cursor_start_buffer()

                self.g_pressed = False
                return

            # 'G'
            if event.keyval == Gdk.keyval_from_name('G'):
                # '<number>G' cursor to that line number
                if repeat > 1 or (repeat == 1 and len(self.argument_digits) == 1):
                    self.cursor_go_to_line(repeat)
                # 'G' cursor to end of buffer
                else:
                    self.cursor_end_buffer()
                return

            for i in range(repeat):
                # 'j' cursor down
                if event.keyval == Gdk.keyval_from_name('j'):
                    self.cursor_down()
                # 'k' cursor up
                elif event.keyval == Gdk.keyval_from_name('k'):
                    self.cursor_up()
                # 'J' 15j
                elif event.keyval == Gdk.keyval_from_name('J'):
                    for x in range(15):
                        self.cursor_down()
                # 'K' 15k
                elif event.keyval == Gdk.keyval_from_name('K'):
                    for x in range(15):
                        self.cursor_up()
                # 'l' cursor right
                elif event.keyval == Gdk.keyval_from_name('l'):
                    self.cursor_right()
                # 'h' cursor left
                elif event.keyval == Gdk.keyval_from_name('h'):
                    self.cursor_left()
                # 'e' cursor to next end of word
                elif event.keyval == Gdk.keyval_from_name('e'):
                    self.cursor_right_word_end()
                # 'w' cursor to next start of word
                elif event.keyval == Gdk.keyval_from_name('w'):
                    self.cursor_right_word_start()
                # 'b' cursor to previous start of word
                elif event.keyval == Gdk.keyval_from_name('b'):
                    self.cursor_left_word_start()
                # '$' cursor to end of line
                elif event.keyval == Gdk.keyval_from_name('dollar'):
                    self.cursor_end_line()
                # '0' cursor to start of line
                elif event.keyval == Gdk.keyval_from_name('0'):
                    self.cursor_start_line()
        finally:
            if not self.g_pressed:
                self.gg_argument = 0

    def add_argument_digit(self, digit):
        self.argument_digits.append(digit)

    def update_cursor_iterator(self):
        self.buf = self.view.get_buffer()
        self.it = self.buf.get_start_iter()
        self.it.set_offset(self.buf.props.cursor_position)

    def cursor_down(self):
        if not self.it.ends_line():
            self.line_offset = self.it.get_line_offset()
        self.it.forward_line()
        self.view.scroll_to_iter(self.it, 0.0, False, 0.0, 1.0)
        self.cursor_maintain_line_offset()

    def cursor_up(self):
        if not self.it.ends_line():
            self.line_offset = self.it.get_line_offset()
        self.it.backward_line()
        self.view.scroll_to_iter(self.it, 0.0, False, 0.0, 0.0)
        self.cursor_maintain_line_offset()

    def cursor_right(self):
        if not self.it.ends_line():
            self.it.forward_char()

    def cursor_left(self):
        if not self.it.starts_line():
            self.it.backward_char()

    def cursor_end_line(self):
        while not self.it.ends_line():
            self.it.forward_char()

    def cursor_start_line(self):
        while not self.it.starts_line():
            self.it.backward_char()

    def cursor_maintain_line_offset(self):
        for i in range(0, self.line_offset):
            if self.it.ends_line():
                break
            self.it.forward_char()

    def cursor_right_word_end(self):
        self.it.forward_word_end()
        self.view.scroll_to_iter(self.it, 0.0, False, 0.0, 1.0)

    def cursor_right_word_start(self):
        if not self.it.ends_word():
            self.it.forward_word_end()
        while not self.it.starts_word() and not self.it.is_end():
            self.it.forward_char()
        self.view.scroll_to_iter(self.it, 0.0, False, 0.0, 1.0)

    def cursor_left_word_start(self):
        self.it.backward_word_start()
        self.view.scroll_to_iter(self.it, 0.0, False, 0.0, 0.0)

    def cursor_insert_line_above(self):
        self.cursor_start_line()
        self.buf.place_cursor(self.it)
        #TODO: probably not portable
        self.buf.insert_at_cursor("\n", 1)
        self.update_cursor_iterator()
        self.cursor_up()
        self.view.scroll_to_iter(self.it, 0.0, False, 0.0, 0.0)
        self.insert_mode()

    def cursor_insert_line_below(self):
        self.cursor_end_line()
        self.buf.place_cursor(self.it)
        #TODO: probably not portable
        self.buf.insert_at_cursor("\n", 1)
        self.update_cursor_iterator()
        self.view.scroll_to_iter(self.it, 0.0, False, 0.0, 1.0)
        self.insert_mode()

    def cursor_end_buffer(self):
        self.it.set_line(self.buf.get_line_count())
        self.cursor_end_line()
        self.view.scroll_to_iter(self.it, 0.0, False, 0.0, 0.0)

    def cursor_start_buffer(self):
        self.it.set_line(0)
        self.cursor_start_line()
        self.view.scroll_to_iter(self.it, 0.0, False, 0.0, 0.0)

    def cursor_delete_char(self):
        tmp_it = self.buf.get_start_iter()
        tmp_it.assign(self.it)
        tmp_it.forward_char()
        self.buf.delete(self.it, tmp_it)

    def cursor_go_to_line(self, line_num):
        self.it.set_line(line_num - 1)
        self.view.scroll_to_iter(self.it, 0.0, False, 0.0, 0.0)

    # returns string containing spaces and tabs of indent of the current line
    def get_line_indent(self):
        indent_str = ""

        self.cursor_start_line()
        while self.it.get_char() == " " or self.it.get_char() == "\t":
            indent_str += self.it.get_char()
            self.it.forward_char()
        return indent_str
