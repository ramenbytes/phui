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

# Don't want to spin up a nested access function right now. Though we will
# need that later... This should be helpful:
# https://stackoverflow.com/questions/28225552/is-there-a-recursive-version-of-the-dict-get-built-in/52260663#52260663

def get_leaf(root, *keys):
    '''Performs nested access on root using keys'''
    access = lambda x, y: x[y]
    return functools.reduce(access, keys, root)

def set_leaf(root, keys, value):
    '''Given root, a possibly nested dict, and the list of keys (the 'path') needed
to access value, will follow that path, creating any missing nested
dictionaries, until it reaches the proper depth and can insert the value. If the
value at the specified path already exists, it is overwritten. Returns the
updated dictionary.

Example:
    set_leaf(dict(), ['photon_data', 'detectors'], "hi!")

    => {'photon_data':{'detectors':'hi!'}}

    '''
    leaf_index = len(keys) - 1

    # this points to the current dictionary we are trying to create/set a key
    # in.
    current_node = root

    for nth in range(leaf_index + 1):
        if nth == leaf_index:
            # for this case, we've reached the end of our path and need to insert the leaf value
            if type(current_node) == list:
                print(keys, current_node)
            current_node[keys[nth]] = value
        else:
            # We still have more keys to go, so create a nested dictionary,
            # stomping on the current non-dict value if necessary.

            # get the current value, defaulting to a dict if it doesn't exist.
            next_node = current_node.get(keys[nth], dict())
            if type(next_node) != dict:
                # we need to stomp on the current value, since we want it to be
                # a dictionary now.
                next_node = dict()

            # insert it in the dictionary we're current inside
            current_node[keys[nth]] = next_node
            # and set things up to descend into this new dictionary on the next iteration
            current_node = next_node

    return root

def get_leaf(root, *keys):
    '''Performs nested access on root using keys'''
    access = lambda x, y: x[y]
    return functools.reduce(access, keys, root)
