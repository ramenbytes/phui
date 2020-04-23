#!/usr/bin/env python3
# For metadata file
import yaml
# For gui
from tkinter import *
from tkinter import ttk
# For conversion library
import phconvert as ph

# Here's a thought: lets focus on getting a nice gui for editing the YAML
# metadata. Link to the data groups:
# https://photon-hdf5.readthedocs.io/en/latest/phdata.html
#
# Would want ways to selectively show groups, possibly more granular options too
# like only supplied options, mandatory, optional, so on. I think different
# setups have different requirements too.
def run(width='300', hight='200'):
    root = Tk()
    root.geometry(width + 'x' + hight)
    root.mainloop()
