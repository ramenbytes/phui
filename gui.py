#!/usr/bin/env python3
# For gui
# from tkinter import *
# from tkinter import ttk

import yaml
from pathlib import Path
import matplotlib.pyplot as plt

import phconvert as phc

# Here's a thought: lets focus on getting a nice gui for editing the YAML
# metadata. Link to the data groups:
# https://photon-hdf5.readthedocs.io/en/latest/phdata.html
#
# Would want ways to selectively show groups, possibly more granular options too
# like only supplied options, mandatory, optional, so on. I think different
# setups have different requirements too.
# def run(width='300', hight='200'):
#     root = Tk()
#     root.geometry(width + 'x' + hight)
#     root.mainloop()

# possible folding frame implementation starting point:
# https://stackoverflow.com/questions/13141259/expandable-and-contracting-frame-in-tkinter
# What is the license on StackOverflow postings?
# Creative Commons type: https://stackoverflow.com/help/licensing
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

# On second thought, I think it may make more sense to develop the logic and
# then form the gui around that. This is opposed to the gui-first attitude I've
# had so far. If I could somehow have convenient way of dealing with the idea of
# commands as opposed to raw events, that seems like it would be lovely. From
# here on out, probably better to focus on core conversion logic and bootstrap
# from there. As much as things can be bootstrapped in python...

# Current goal: Point and shoot file conversion. i.e, convert(file) -> converted file
# Current state: ?
# Answer: Not very nice. Inordinate amount of work just to convert a file,
# involving setup of all the metadata. At least from the look of things.
data_file = Path('./data/0023uLRpitc_NTP_20dT_0.5GndCl.sm')
meta_file = data_file.with_suffix('.yml')
