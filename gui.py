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
data_file = Path('./data/0023uLRpitc_NTP_20dT_0.5GndCl.sm')
meta_file = data_file.with_suffix('.yml')
