#!/usr/bin/env python3
# For gui
from tkinter import *
from tkinter import ttk
from tkinter import filedialog

import yaml
from pathlib import Path
# debugging
import pdb

# unified conversion
import unified_conversion as uc

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

# /Not/ setting this permits tkinter to pick the best size for the window, such
# that all widgets fit. It will /also/ resize when a widget gets bigger, say
# from the filename growing bigger in the label. Overall, generally a win.
# root.geometry('600x400')

# Make it resizeable after the we've made it the specified size? Deal with later.
# root.resizable()
# if we resize the window, these lines let our frame resize too
# root.columnconfigure(0, weight=1)
# root.rowconfigure(0, weight=1)

# conversion widget frame
target_frame = Frame(root)
target_frame.grid(column=0,row=0,sticky=(N, S, E, W))

# button for conversion
chosenfile = StringVar()
chosenfile.set("<choose a target>")
targetlabel = Label(target_frame, textvariable=chosenfile)
# the padding is to provide space between the label and the following button
targetlabel.grid(column=0,padx=10)

def make_callback(finder,stringvar):
    '''Returns a closure over finder and stringvar. finder must be a function that
returns a filepath, and stringvar must be a StringVar object. The returned
closure, when called, will set the stringvar text to the name returned by
finder.'''
    def callback():
        stringvar.set(finder())

    return callback

filebutton = Button(target_frame, text="Select a file", command=make_callback(filedialog.askopenfilename, chosenfile))
filebutton.grid(column=1,row=0)

dirbutton = Button(target_frame, text="Select a directory", command=make_callback(filedialog.askdirectory,chosenfile))
dirbutton.grid(column=2,row=0)

descriptionlabel = Label(target_frame, text="Enter a description of the data:")
descriptionlabel.grid(row=1,sticky=W)

description = Text(target_frame,height=5)
description.grid(row=2)

def ensure_description(description):
    '''Ensures that the description string we got is non-blank, returning it if so.
Otherwise, errors with an explanatory message.'''
    assert len(description.strip()) != 0, "The description cannot be blank"
    return description

convertbutton = Button(target_frame, text="Convert",
                       command=lambda: uc.convert(chosenfile.get(),
                                                  data_fragment =
                                                  {'description': ensure_description(description.get('1.0','end'))}) )
convertbutton.grid(column=3,row=0)

root.mainloop()
