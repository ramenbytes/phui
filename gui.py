#!/usr/bin/env python3
# For gui
# from tkinter import *
# from tkinter import ttk

import yaml
from pathlib import Path
import matplotlib.pyplot as plt
import phconvert as phc
# debugging
import pdb

# Current goal: Point and shoot file conversion. i.e, convert(file) -> converted file
# Current state: ?
# Answer: Not very nice. Inordinate amount of work just to convert a file,
# involving setup of all the metadata. At least from the look of things.


# Link to the data groups:
# https://photon-hdf5.readthedocs.io/en/latest/phdata.html
data_file = Path('./data/0023uLRpitc_NTP_20dT_0.5GndCl.sm')
meta_file = data_file.with_suffix('.yml')

# load metadata file
with open(meta_file) as f:
    metadata = yaml.full_load(f)

# looks like the way you create the photonHDF5 files is by loading all info into
# nested dicts then passing that nest to the save function
