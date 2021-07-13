#!/usr/bin/env python3
# For gui
from tkinter import *
from tkinter import ttk
from tkinter import filedialog

import os
import yaml
from pathlib import Path
# debugging
import pdb

# unified conversion
import unified_conversion as uc

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

root = Tk()
root.title('PHUI')
# Forbidding resizing prevents stumpwm full-sizing the window. Presumably it
# would work for other window managers, based on the docs.
root.resizable(False,False)

# /Not/ setting this permits tkinter to pick the best size for the window, such
# that all widgets fit. It will /also/ resize when a widget gets bigger, say
# from the filename growing bigger in the label. Overall, generally a win.
# root.geometry('600x400')

# Make it resizeable after the we've made it the specified size? Deal with later.
# root.resizable()
# if we resize the window, these lines let our frame resize too
# root.columnconfigure(0, weight=1)
# root.rowconfigure(0, weight=1)

class target:

    def ensure_description(self,description):
        '''Ensures that the description string we got is non-blank, returning it if so.
        Otherwise, errors with an explanatory message.'''
        assert len(description.strip()) != 0, "The description cannot be blank"
        return description

    def convert(self):
        # TODO: now that we want to support metadata files, this is too
        # simplistic. We need to 'parse' the gui data into arguments for
        # conversion, and handle missing data.

        # Plan: break all this logic into a nested function that handles the conversion? Do we even need one?
        data_fragment = {'description': self.ensure_description(self.description.get('1.0','end'))}
        convert = lambda filename: uc.convert(filename, data_fragment = data_fragment)

        filename = self.chosenfile.get()
        metadata_file = self.chosen_metadata.get()

        if os.path.isfile(filename):
            convert(filename)
            print('done with current file')
        elif os.path.isdir(filename):
            dirname = filename
            # For batch conversion, we shouldn't require metadata, and just let
            # the conversion routines pick up the apropriately named files in
            # the directory. We should still allow the option though, perhaps
            # applying it as a "global option"? Local files override the
            # globals?
            #
            # for more info on this library: https://stackoverflow.com/questions/3160699/python-progress-bar
            # import tqdm
            # for x in tqdm.tqdm(os.listdir(dirname)):
            for x in os.listdir(dirname):
                if uc.convertable_p(x):
                    convert(dirname + '/' + x)
                    print('done with current file')

        return

    def __init__(self,parent,row=0,column=0):
        # conversion widget frame
        self.target_frame = Frame(parent)
        self.target_frame['borderwidth'] = 2
        self.target_frame['relief'] = 'raised'
        self.target_frame.grid(row=row,column=column,sticky=(N, S, E, W))

        # button for conversion
        self.chosenfile = StringVar()
        self.chosenfile.set("<choose a target>")
        self.targetlabel = Label(self.target_frame, textvariable=self.chosenfile)
        # the padding is to provide space between the label and the following button
        self.targetlabel.grid(column=0,padx=(0,1),sticky=(W,E,N,S))
        self.targetlabel['relief'] = 'sunken'

        def make_callback(finder,stringvar):
            '''Returns a closure over finder and stringvar. finder must be a function that
        returns a filepath, and stringvar must be a StringVar object. The returned
        closure, when called, will set the stringvar text to the name returned by
        finder.'''
            def callback():
                stringvar.set(finder())

            return callback

        self.filebutton = Button(self.target_frame, text="Select a file" , command=make_callback(filedialog.askopenfilename, self.chosenfile))
        self.filebutton.grid(column=1,row=0,sticky=(W,E))

        self.dirbutton = Button(self.target_frame, text="Select a directory", command=make_callback(filedialog.askdirectory, self.chosenfile))
        self.dirbutton.grid(column=2,row=0)

        self.chosen_metadata = StringVar()
        self.chosen_metadata.set("<choose optional metadata file>")
        self.metadata_label = Label(self.target_frame, textvariable=self.chosen_metadata)
        self.metadata_label.grid(row=1,column=0, padx=(0,1), sticky=(W,E,N,S))
        self.metadata_label['relief'] = 'sunken'

        self.metadata_button = Button(self.target_frame, text="Select metadata file", command=make_callback(filedialog.askopenfilename, self.chosen_metadata))
        self.metadata_button.grid(column=1, columnspan=2, row=1,sticky=(W,E))

        self.descriptionlabel = Label(self.target_frame, text="Enter a description of the data:")
        self.descriptionlabel.grid(row=2,sticky=W,pady=(5,0))

        self.description = Text(self.target_frame,height=3)
        self.description.grid(row=3,pady=(0,2),padx=(0,1))

        self.convertbutton = Button(self.target_frame, text="Convert",
                            command=self.convert)
        self.convertbutton.grid(column=3,row=0,rowspan=2,sticky=(N,S))

        return

test = target(root,row=0,column=0)
test2 = target(root,row=1,column=0)

root.mainloop()
