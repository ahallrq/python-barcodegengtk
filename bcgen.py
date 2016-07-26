#!/bin/python3

# MIT License
# 
# python-barcodegengtk: A GTK frontend for PyUPC-EAN
# Copyright (c) 2016 Andrew Hall (iownall555)
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GdkPixbuf, GObject, Gdk
import upcean
import random

class MainUi:
    def __init__(self, glade_file):
        self.builder = Gtk.Builder()
        self.builder.add_from_file(glade_file)
        self.get_objects()
        self.create_signal_handler()
        self.builder.connect_signals(self.signal_handler)
        self.create_barcode_types()

        tree_iter = self.bctype.get_active_iter()
        if tree_iter != None:
            self.active_type = self.bctype.get_model()[tree_iter][0]
            self.bctext.set_max_length(self.barcode_types[self.active_type][0])
            self.bctext.set_text("")
        self.generate("Barcode Generator")

    def get_objects(self):
        self.window = self.builder.get_object("mainwindow")
        self.bcgen = self.builder.get_object("bcgen")
        self.bctext = self.builder.get_object("bctext")
        self.bctype = self.builder.get_object("bctype")
        self.bcimage = self.builder.get_object("bcimg")
        self.bcmenu = self.builder.get_object("bcmenu")
        self.bcsavedialog = self.builder.get_object("bcsavedialog")

    def menuEvent(self, image, data):
        if (data.button == 3):
            self.bcmenu.popup(None, None, None, None, data.button, data.time)

    def bcMenuCopyEvent(self, data):
        clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)
        clipboard.set_image(self.bcpixbuf)
        clipboard.store()

    def bcMenuPrintEvent(self, data):
        pass

    def bcMenuSaveEvent(self, data):
        self.bcsavedialog.run()
        self.bcsavedialog.hide()

    def generate(self, text):
        if (text == ""):
            text = self.barcode_types[self.active_type][4]

        typedict = self.barcode_types[self.active_type]
        if (typedict[3] == "discrete") and (len(text) < typedict[0]):
            text = text.ljust(typedict[0], "0")
        elif (typedict[3] == "continuous"):
            if (typedict[2] == "itf"):
                if (len(text) < 6):
                    text = text.ljust(6, "0")
                else:
                    if (len(text) % 2 == 1):
                        text += "0"
            elif (len(text) == 0):
                text = self.barcode_types[self.active_type][4]

        if (typedict[2] == "codabar"): #I should probably improve this.
            text = "A" + text + "B"

        image = upcean.oopfuncs.barcode(self.barcode_types[self.active_type][2], text).draw_barcode(2)
        image.save("/tmp/bc.png")
        self.bcpixbuf = GdkPixbuf.Pixbuf.new_from_file("/tmp/bc.png")
        self.bcimage.set_from_pixbuf(self.bcpixbuf)

    def create_signal_handler(self):
        self.signal_handler = {
                                "onDeleteWindow": Gtk.main_quit,
                                "entryInsert": self.entryInsert,
                                "entryChanged": self.entryChanged,
                                "typeChanged": self.typeChanged,
                                "bcMenuEvent": self.menuEvent,
                                "bcMenuCopyEvent": self.bcMenuCopyEvent,
                                "bcMenuSaveEvent": self.bcMenuSaveEvent,
                                "bcMenuPrintEvent": self.bcMenuPrintEvent
                              }

    def create_barcode_types(self):
        self.barcode_types = {
                                "Codabar": [64, "1234567890-./:$+", "codabar", "continuous", "1234567890"],
                                "Code11" : [64, "1234567890-", "code11", "continuous", "1234567890-"],
                                "Code39" : [64, "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789abcdefghijklmnopqrstuvwxyz-.$/+% ", "code39", "continuous", "Barcode Generator"],
                                "Code93" : [64, "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789abcdefghijklmnopqrstuvwxyz-.$/+% ", "code93", "continuous", "Barcode Generator"],
                                "EAN-2"  : [2, "1234567890", "ean2", "discrete", "12"],
                                "EAN-5"  : [5, "1234567890", "ean5", "discrete", "12345"],
                                "EAN-8"  : [8, "1234567890", "ean8", "discrete", "12345678"],
                                "EAN-13" : [13, "1234567890", "ean13", "discrete", "1234567890123"],
                                "ITF"    : [64, "1234567890", "itf", "continuous", "123456"],
                                "ITF-14" : [14, "1234567890", "itf14", "discrete", "12345678901234"],
                                "MSI"    : [64, "1234567890", "msi", "continuous", "1234567890"],
                                "STF"    : [64, "1234567890", "stf", "continuous", "1234567890"],
                                "UPC-A"  : [12, "1234567890", "upca", "discrete", "123456789012"],
                                "UPC-E"  : [8, "1234567890", "upce", "discrete", "12345678"]
                             }

    def entryChanged(self, entry):
        self.generate(entry.get_text())

    def entryInsert(self, entry, text, length, position):
        position = entry.get_position() # Because the method parameter 'position' is useless

        # Build a new string with allowed characters only.
        result = ''.join([c for c in text if c in self.barcode_types[self.active_type][1]])

        # The above line could also be written like so (more readable but less efficient):
        # result = ''
        # for c in text:
        #     if c in string.hexdigits:
        #         result += c

        if (result != '' and (entry.get_text_length() < entry.get_max_length())):
            # Insert the new text at cursor (and block the handler to avoid recursion).
            entry.handler_block_by_func(self.entryInsert)
            entry.insert_text(result, position)
            entry.handler_unblock_by_func(self.entryInsert)

            # Set the new cursor position immediately after the inserted text.
            new_pos = position + len(result)

            # Can't modify the cursor position from within this handler,
            # so we add it to be done at the end of the main loop:
            GObject.idle_add(entry.set_position, new_pos)

        # We handled the signal so stop it from being processed further.
        entry.stop_emission("insert_text")

    def typeChanged(self, combo):
        tree_iter = combo.get_active_iter()
        if tree_iter != None:
            self.active_type = combo.get_model()[tree_iter][0]
            self.bctext.set_max_length(self.barcode_types[self.active_type][0])
            self.bctext.set_text("")

        self.generate(self.bctext.get_text())

if (__name__ == "__main__"):
    MW = MainUi("bcgen.glade")
    MW.window.show_all()

    Gtk.main()
