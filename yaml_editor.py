'''This module provides the editor for our restricted subset of yaml metadata'''

from tkinter import *
from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox

from phconvert.metadata import official_fields_specs

# ok, how do I show users all the options? Also, how to do I automate the
# translation of the specs to a tree, for later use? What I'd like to be able to
# do is to more or less just say
#
# create_entry(dict, '<flattened_path_from_specs', description_list)
#
# to create an entry in the (possibly nested) dictionar(y/ies)
