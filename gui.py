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

# for some reason, stumpwm does not respect the resize when I eval the whole
# buffer. Individually eval'ing each statement does the trick though. ???
root = Tk()
root.title('PHUI')
root.geometry('300x200')
