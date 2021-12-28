#!/usr/bin/env python3
# For gui

from tkinter import *
from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox

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

        filename = self.chosenfile.get() # we take whatever they give us
        kwargs = dict() # initialize to a dictionary for later operations

        # right now, this does not handle batch conversions any differently than single conversions, which is bad.
        if self.chosen_metadata.get() != self.metadata_label_default:
            kwargs["yml_file"] = self.chosen_metadata.get()

        if len(self.description.get('1.0','end').strip()) != 0:
            kwargs["data_fragment"] = {'description': self.ensure_description(self.description.get('1.0','end'))}

        # convert = lambda filename: uc.convert(filename, data_fragment = data_fragment, **kwargs)
        convert = lambda filename: uc.convert(filename, **kwargs)

        try:
            if os.path.isfile(filename):
                print('\n>>>>>>>>>>>>>>>>>>>>>>>>>>>>>starting current file<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<\n')
                convert(filename)
                print('\n<<<<<<<<<<<<<<<<<<<<<<<<<<<<<done with current file>>>>>>>>>>>>>>>>>>>>>>>>>>>>>')
                self.status.set(self.status_prefix + "Converted")
                self.statuslabel.configure(bg='green')
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
                print('\n>>>>>>>>>>>>>>>>>>>>>>>>>>>>>starting current directory<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<\n\n')

                # maybe later we let people specify this file
                progress_file = dirname + "/phui_conversion_progress.log"

                # we'll use this variable to store the names of files we've
                # already converted, and don't need to waste time processing
                # again.
                files_to_skip = []

                # seeing this flag at the start of a log file line means that
                # the conversion was successful
                success_flag = "SUCCESS: "

                # If this flag is at the start of a log file line, then that
                # file's conversion failed. *sad trombone*
                fail_flag = "FAILURE: "

                # Check to see if we already have a progress file. Maybe we
                # later move this block under the conversion's with statement,
                # and instead of checking for file existence just blow through
                # it looking for lines? Hmm... not sure if that makes sense to
                # choose over the current method.
                if os.path.exists(progress_file):
                    with open(progress_file, mode='r') as progress_log:
                        # This line-based solution feels crude. Structured data
                        # might be better/more robust
                        files_to_skip = [line[len(success_flag):].strip()
                                         for line in progress_log.readlines()
                                         if line[:len(success_flag)] == success_flag]

                with open(progress_file, mode='a') as progress_log:

                    unconverted_files = [file for file in os.listdir(dirname) if file not in files_to_skip]

                    for x in unconverted_files:
                        if uc.convertable_p(x):
                            print('\n>>>>>>>>>>>>>>>>>>>>>>>>>>>>>starting current file<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<\n')

                            try:
                                convert(dirname + '/' + x)
                                # upon success, print the filename (relative to our directory) to the progress log
                                print(success_flag + x, file=progress_log)

                            except BaseException as e:
                                # I really think structured data would be
                                # nicer... Saves us from explicitly dealing with
                                # parsing/serialization/etc.
                                print(fail_flag + x + " REASON: " + repr(e), file=progress_log)

                            print('\n<<<<<<<<<<<<<<<<<<<<<<<<<<<<<done with current file>>>>>>>>>>>>>>>>>>>>>>>>>>>>>')

                    self.status.set(self.status_prefix + "Converted")
                    self.statuslabel.configure(bg='green')

                print('\n\n<<<<<<<<<<<<<<<<<<<<<<<<<<<<<done with current directory>>>>>>>>>>>>>>>>>>>>>>>>>>>>>')
            else:
                raise ValueError('The target is not a valid file or directory!')

        # FIXME: This should be way more fine grained and helpful! I wonder what
        # sort of errors won't result in a failed conversion...
        except BaseException as e:
            self.statuslabel.configure(bg='red')
            self.status.set('Failed Conversion')
            # just directly show the user our exception message
            messagebox.showerror(message=repr(e))

        return

    def delete(self):
        # FIXME: If the target is the last one in the frame, then the parent
        # frame isn't resized upon deletion. What gives?
        return self.target_frame.destroy()

    def __init__(self,parent,row=0,column=0):
        # conversion widget frame
        self.target_frame = Frame(parent)
        self.target_frame['borderwidth'] = 3
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
        self.metadata_label_default = "<choose optional metadata file>"
        # this is both our canary and our default display string... how can we change this?
        self.chosen_metadata.set(self.metadata_label_default)
        self.metadata_label = Label(self.target_frame, textvariable=self.chosen_metadata)
        self.metadata_label.grid(row=1,column=0, padx=(0,1), sticky=(W,E,N,S))
        self.metadata_label['relief'] = 'sunken'

        self.metadata_button = Button(self.target_frame, text="Select metadata file", command=make_callback(filedialog.askopenfilename, self.chosen_metadata))
        self.metadata_button.grid(column=1, columnspan=2, row=1,sticky=(W,E))

        self.delete_button = Button(self.target_frame, text="Remove target",
                                    command=lambda: remove_target(self))
        self.delete_button.grid(column=3,row=0,rowspan=2,sticky=(N,W,E,S))

        self.descriptionlabel = Label(self.target_frame, text="Enter a description of the data:")
        self.descriptionlabel.grid(row=2,sticky=W,pady=(5,0))

        self.description = Text(self.target_frame,height=3)
        self.description.grid(row=3,pady=(0,2),padx=(0,1))

        # we'll use this to indicate successful conversion
        # changing the background color can be done this way:
        # https://stackoverflow.com/questions/13588908/dynamically-change-widget-background-color-in-tkinter
        self.status = StringVar()
        # self.status_prefix = "Status: "
        self.status_prefix = ""
        self.status.set(self.status_prefix + "Unconverted")
        self.statuslabel = Label(self.target_frame, textvariable=self.status)
        self.statuslabel.grid(row=4, columnspan=4, sticky=(N,S,E,W))
        self.statuslabel.configure(bg = '#808080') # Set to a dark grey at first

        self.convertbutton = Button(self.target_frame, text="Convert",
                            command=self.convert)
        self.convertbutton.grid(column=1,row=2,rowspan=2,columnspan=3, sticky=(N,S,E,W))

        return

root = Tk()
root.title('PHUI')
# Forbidding resizing prevents stumpwm full-sizing the window. Presumably it
# would work for other window managers, based on the docs.
root.resizable(False,False)

# here we make the frame that will hold all our conversion targets, and make it
# possible to add more
targets_frame = Frame(root)
targets_frame.grid()
# as a thought, we might have to deal with repacking the row numbers if we
# remove target entries
tests = []

def add_target():
    return tests.append(target(targets_frame,row=len(tests),column=0))

def remove_target(target):
    # remove it from the gui
    target.delete()
    # remove it from our list of targets
    return tests.remove(target)

add_button = Button(root,command=add_target,text= "Add a conversion target")
add_button['borderwidth'] = 3
add_button.grid(sticky=(N,S,E,W))

# Provide one target on startup. If they want more, they have the button.
add_target()

root.mainloop()
