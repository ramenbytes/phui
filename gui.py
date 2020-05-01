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

# possible folding frame implementation starting point:
# https://stackoverflow.com/questions/13141259/expandable-and-contracting-frame-in-tkinter
# What is the license on StackOverflow postings?
#
# Creating your own widgets:
# https://mail.python.org/pipermail/tkinter-discuss/2008-August/001602.html
# https://stackoverflow.com/questions/30489308/creating-a-custom-widget-in-tkinter
# https://effbot.org/zone/tkinter3000-wck.htm
# Widget creation kits:
# https://effbot.org/zone/wck-1.htm
# https://pypi.org/project/tkinter3000/
# http://pmw.sourceforge.net/
# https://sourceforge.net/projects/pmw/
