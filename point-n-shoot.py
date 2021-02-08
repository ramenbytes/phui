''' A module for painless datafile conversion with phconvert.'''

import os
from pathlib import Path
import yaml
import phconvert as phc

with open(os.path.expanduser('~/weisslab/phui/dumped.yml'), mode='r') as f:
    # unsafe allows arbitrary code execution, meaning creation of numpy types
    # can happen. Since we save a numpy float, this is desired here. Still, a hack.
    snarf = yaml.unsafe_load(f)

# test data
input_filename = Path('data/0023uLRpitc_NTP_20dT_0.5GndCl.sm')

# poke photon data into file
snarf['photon_data']['timestamps'], snarf['photon_data']['detectors'] = phc.smreader.load_sm(input_filename)

### Now, I want to package the above into a function taking just a filename with
### sane defaulting and optional specifications for defaults and added metadata keys.

## This var is more or less a dispatch table... Is there a better way?
##
## Note: .phu files aren't here because the loader doesn't have the same return
## type as the other loaders. Do those get converted too?
loaders = {'.sm' : phc.smreader.load_sm, '.ht3' : phc.pqreader.load_ht3,
           '.ptu' : phc.pqreader.load_ptu, '.pt3' : phc.pqreader.load_pt3,
           '.t3r' : phc.pqreader.load_t3r, '.set' : phc.bhreader.load_set,
           '.spc' : phc.bhreader.load_spc}

def load (file):
    '''General interface for loading data files that return a tuple of
    timestamps, detectors, and optionally something else.'''
    file = Path(file)
    return loaders[file.suffix](file)

def load_and_poke(file, yml_file=False):
    input_file = Path(file)

    if yml_file is False:
        yml_file = input_file.with_suffix('.yml')

    yml_file = Path(yml_file)

    assert yml_file.is_file()
    with open(yml_file) as meta_file:
        metadata = yaml.unsafe_load(meta_file)

        ## Call the function associated with the file's type to load the data
        timestamps, detectors = load(input_file)
        # FIXME This part seems rather brittle. Also, apparently if the parent
        # key doesn't exist you can't create the subkey. Nice.
        metadata['photon_data']['timestamps'] = timestamps
        metadata['photon_data']['detectors'] = detectors

    return metadata

### Want to have argument for metadata dictionary fragement that gets merged
### with file data. Need to be able to merge dictionaries...
### Looks promising:
### https://stackoverflow.com/questions/7204805/how-to-merge-dictionaries-of-dictionaries/25270947#25270947
def convert(input, output=False, yaml_file=False):
    '''Takes input file and converts it to Photon-HDF5, outputting to output.
    yaml_file is a file containing all the necessary metadata as required or
    allowed by phconvert. Both output and yaml_file default to input's value
    with the appropiate file type suffix.'''
    if not output:
        output = Path(input).with_suffix('.hdf5')

        data = load_and_poke(input, yaml_file)
        phc.hdf5.save_photon_hdf5(data, h5_fname=output, overwrite=True, close=True)
        return

#### ok, dictionary merging
### What is wanted? For the user to be able to pass fragments of the final
### dictionary file structure to override the options loaded from the metadata
### file or supplement missing ones. Don't think it makes sense to require
### metadata to be in file, whether placed there before conversion or not.
### Because, it will be plainly available in the hdf5 file. It's not like
### compile options which (to my knowledge) are hard to recover after the fact.
### There may be issues though if the user expects the yml files to be the sole
### sources of truth, since they could be out of sync with the hdf5. Never the
### less, I think it would be better to not place this restriction until a
### better reason than 'users may not be organized' comes up.

## ok, need a way to merge two non-colliding dictionaries. Can be accomplished
## with update():
test = dict()
test.update({3: 4, 5: 6})
## this will overwrite the colliding keys in test though, so there must not be any.

## What about for collision cases?
## Well, we only want to override leaves and not nodes for our use case. So if
## nodes collide and their subnodes/leaves don't, add the subnodes/leaves of one to
## the other. If there is a collision with subnodes/leaves, repeat the process
## until leaves (which terminate the nesting) are reached, in which case replace
## the leave of the yielding dicitonary with that of the master.
##
## Thinking I'll first write the recursive version, then transform to iterative.
## Maybe, first transform to tail recursive? If possible?
##
## Another note, apparently you shouldn't mutate dictionary while modifying it?
## Does this mean I need to return a copy? Setting nodes doesn't cause problems,
## but adding and removing nodes might! Our merge will both set nodes and add
## nodes, copy it is. Note: A possible optimization at a later date is minimal
## copying, possibly only when adding keys?
##
## Think I may need to emulate a stack via pushing stuff onto lists for later...
## How could I make all the calls tail recursive?

def _recursive_merge(dom,sub):
    '''WIP: Recursively merge dictionary dom into sub. If colliding keys are for
    dictionaries, merge those too. Otherwise use dom's value. Order is NOT preserved.'''

    ## We modify sub, but iterate over dom. Sidesteps issues with mutating iterators?
    for key in dom:
        ## Unless there are colliding nested dictionaries, use dom's value.
        if (key in sub) and (type(dom[key]) is type(sub[key]) is dict):
            recursive_merge(dom[key], sub[key]) # horrid memory performance implications
        else:
            sub[key] = dom[key]
    return sub

def recursive_merge(source_dict, destination_dict):
    '''Destructively merge source_dict into destination_dict. When there is a key
    collision, destination_dict's value will be overwritten with
    source_dict's with one exception. If the values associated with the shared
    key are both dictionaries themselves, then the one from source_dict is
    destructively merged into the one from destination_dict in the same manner
    as before. All nested dictionaries with a mutual keypath (the chain of keys
    used to access them) are merged in this manner.'''

    ## some convenience functions
    def push (item, sequence):
        '''Insert item at the beginning of sequence.'''
        sequence.insert(0,item)
        return item

    def pop (sequence):
        '''Pop and return 0th element of sequence.'''
        return sequence.pop(0)

    # This will hold the dictionaries that need to be merged. As we come accross
    # nested dictionaries with mutual keypaths we push them onto this list to be
    # merged later.
    dict_pairs_to_merge = [(source_dict, destination_dict)]

    while dict_pairs_to_merge:
        # Grab the two dictionaries being merged on this pass through the loop.
        # Any nested dicts with colliding keys will themselves be merged in
        # another pass.
        current_source, current_destination = pop(dict_pairs_to_merge)

        # add current_source's keys to current_destination, pushing any collisions of nested
        # dictionaries onto a list to merge later.
        for key in current_source:
            ## possibly nested dictionaries
            source_val = current_source[key]
            destination_val = current_destination.get(key)  # guard against missing key

            if (dict is type(source_val) is type(destination_val)):
                # We have a key collision with nested dicts for values. We'll merge them later.
                push((source_val, destination_val), dict_pairs_to_merge)
            else:
                # Either the values weren't both dicts or the key wasn't in
                # destination_dict. Use source_dict's value.
                current_destination[key] = source_val

    return destination_dict
