#!/usr/bin/env python3
# For gui
from tkinter import *
from tkinter import ttk
from tkinter import filedialog

import yaml
from pathlib import Path
# debugging
import pdb

def run(width='300', hight='200'):
    # Creates the top-level widget and tcl process. We see a window pop up
    # because of the creation of the top-level widget.
    root = Tk()
    # Sets the dimensions of our new window
    root.geometry(width + 'x' + hight)
    # Starts the event loop for the associated tcl process. This is a blocking call!
    root.mainloop()

def root_with_geometry(width='300',height='200'):
    root = Tk()
    root.geometry(str(width) + 'x' + str(height))
    return root

root = Tk()
root.title('PHUI')
# Forbidding resizing prevents stumpwm full-sizing the window. Presumably it
# would work for other window managers, based on the docs.
root.resizable(False,False)
root.geometry('600x400')

# Make it resizeable after the we've made it the specified size? Deal with later.
# root.resizable()
# if we resize the window, these lines let our frame resize too
# root.columnconfigure(0, weight=1)
# root.rowconfigure(0, weight=1)

# conversion widget frame
target_frame = Frame(root)
target_frame.grid(column=0,row=0,sticky=(N, S, E, W))

# button for conversion
targetlabel = Label(target_frame, text="<choose a target>")
# the padding is to provide space between the label and the following button
targetlabel.grid(column=0,padx=10)

def make_callback(finder,label):
    '''Returns a closure over finder and label. finder must be a function that
returns a filepath, and label must be a Label object. The returned closure, when
called, will set the label's text to the name returned by finder. '''
    def callback():
        targetname = finder()
        label.configure(text = targetname)

    return callback

filebutton = Button(target_frame, text="Select a file", command=make_callback(filedialog.askopenfilename, targetlabel))
filebutton.grid(column=1,row=0)

dirbutton = Button(target_frame, text="Select a directory", command=make_callback(filedialog.askdirectory,targetlabel))
dirbutton.grid(column=2,row=0)
