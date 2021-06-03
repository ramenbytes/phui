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
