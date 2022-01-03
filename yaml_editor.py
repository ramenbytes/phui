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

# I'm thinking that I can use the spec tree to store the user input too. When
# given the user input, add it as the third element of the list holding the
# description. Then, we can just yank it out later when creating the metadata.
#
# Hmm... that would mean that to get the metadata ready for conversion, we'd
# need to walk the tree replacing each list with the user input. We'd have to
# "parse" it to deal with null inputs... Maybe, instead of storing the user data
# in the tree, which only really works for when we have one single conversion
# target, we instead build up the metadata dictionary bit by bit as the user
# inputs values. Yeah, let's do that. Much less stupid than the other option in
# light of the fact that we could have multiple conversion targets all
# referencing the same spec tree.
#
# Also, to avoid the issue of scrolling in the main gui window (for now) I think
# it would work better to pop out to a new window showing the metadata tree and
# the option to edit/add entries. I think the major piece of helper code will be
# the create_entry() function from above. So, let's do that.
#
# Also, we should check and see what fields are available as metadata, and which
# fields are pulled from the files.

# Ok, it looks like the raw data goes into photon_data. Also, by using the
# loader functions from phc.loader, it looks like we are already populating
# /setup with default values. So, we'll definitely want to show those fields to
# the user for editing. But, we won't show the photon_data field.

def set_leaf(root, path, value):
    '''Given root, possibly nested dict, and the list of keys (the 'path') needed to
access value, will follow the path, creating any missing nested dictionaries,
until it reaches the proper depth and can insert the value. If the value at the
specified path already exists, it is overwritten.

Example:
    set_leaf(dict(), ['photon_data', 'detectors'], "hi!")

    => {'photon_data':{'detectors':'hi!'}}

    '''
    path_length = len(path)


    return 42
