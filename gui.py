#!/usr/bin/env python3
# For gui
from tkinter import *
from tkinter import ttk

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
root.geometry('300x200')

# Make it resizeable after the we've made it the specified size? Deal with later.
# root.resizable()

# button for conversion
label = Label(root, text="<choose a file>")
# label.pack()
label.grid(column=0)

def callback():
    label.configure(text = "Converted!")

button = Button(root, text="Convert", command=callback)
# button.pack()
button.grid(column=1,row=0)
