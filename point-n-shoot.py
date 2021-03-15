'''
A module for painless datafile conversion with phconvert.

To convert a file, use the convert() function.

To load the data into a dictionary, use load().

If you have fragments of data/metadata to merge into the data loaded from a
file, recursive_merge() might be handy.

Finally, if you want to add support for a new file type, add a new entry to the
'loaders' dictionary with the file suffix as the key and a function returning
the file data in a dictionary suitable for passing to
phconvert.hdf5.save_photon_hdf5(). The suffix must include the '.', so for
example '.sm' for the data file format in use at Weiss Lab.
'''

import os
# from pathlib import Path
# import yaml
import phconvert as phc

# with open(os.path.expanduser('~/weisslab/phui/dumped.yml'), mode='r') as f:
#     # unsafe allows arbitrary code execution, meaning creation of numpy types
#     # can happen. Since we save a numpy float, this is desired here. Still, a hack.
#     snarf = yaml.unsafe_load(f)

def compose(g, f):
    "Simple composition of monadic functions."
    return lambda x: g(f(x))

def first_only(loader_function):
    "Returns a new function that will only return the first value of the tuple that loader_function returns"
    return compose(lambda x: x[0] ,loader_function)

# these functions don't return a single dictionary, and for now we only want the
# first item of the returned tuple
pq_loader = first_only(phc.loader.nsalex_pq)
bh_loader = first_only(phc.loader.nsalex_bh)

loaders = {'.sm' : phc.loader.usalex_sm,
           # TODO: Deal with (and expose?) the second, unmentioned dict that is
           # returned for picoquant files
           '.ht3' : pq_loader,
           '.ptu' : pq_loader,
           '.pt3' : pq_loader,
           '.t3r' : phc.loader.nsalex_t3r,
           # TODO: Expose an interface for including the .set file. Could it be
           # done generally, for files that have extra data? HOFs?
           '.set' : bh_loader,
           '.spc' : bh_loader}

def extension(file):
    "Returns the extension of a file path"
    return os.path.splitext(file)[1]

# TODO: confirm which files didn't successfully convert without adding a description
def load (file):
    '''General interface for loading the data from supported filetypes. Returns
    a dictionary containing the file data which may be passed to
    phconvert.hdf5.save_photon_hdf5(). It may be incomplete, for example it may
    not have a description if the file didn't, but it will not be malformed.'''
    return loaders[extension(file)](file)

def filename(file):
    "Returns the filename of a file path"
    return os.path.splitext(file)[0]

# for some reason, the "trace" test file does not successfully load with the
# high-level loaders. Says there is is a missing laser repetition rate in the
# metadata. Edge case to deal with later?
def convert(input, *args, output=False, data_fragment=False):
    '''Takes input file and converts it to Photon-HDF5, outputting to output. output
    defaults to input's value with the appropiate file type suffix. If
    data_fragment is provided, it is interpreted as a piece of the Photon-HDF5
    data hierarchy, with top-level entries corresponding to top-level
    Photon-HDF5 fields. The values it provides will be spliced into the data
    obtained from the photon data file, preserving any entries not explicitly
    provided. See recursive_merge() for more details.'''
    if not output:
        output = filename(input) + '.hdf5'

    data = load(input)
    # use the provided fragment to overwrite/fill in fields
    if data_fragment:
        recursive_merge(data_fragment, data)

    phc.hdf5.save_photon_hdf5(data, h5_fname=output, overwrite=True, close=True)
    return

def recursive_merge(source_dict, destination_dict):
    '''
    Destructively merge source_dict into destination_dict. When there is a key
    collision, destination_dict's value will be overwritten with
    source_dict's with one exception. If the values associated with the shared
    key are both dictionaries themselves, then the one from source_dict is
    destructively merged into the one from destination_dict in the same manner
    as before. All nested dictionaries with a mutual keypath (the chain of keys
    used to access them) are merged in this manner.

    Example:

        In: recursive_merge({'inner':{3:'three'}}, # the source dictionary
                            {'inner':{4:'four'}})  # the dictionary that will be modified

        # the two inner dictionaries are merged!
        Out: {'inner': {4: 'four', 3: 'three'}}

        # without recursive merging it would have turned out like this:
        Out: {'inner':{3:'three'}}
        # since the entry for 'inner' in the dictionary would have been
        # replaced with the entry for 'inner' in the source dictionary.
    '''


    ## some convenience functions
    def push (item, sequence):
        '''Insert item at the beginning of sequence, returning the added item.'''
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

        # Destructivley add current_source's entries to current_destination. If there are
        # nested dictionaries with colliding keys, push them onto a list to merge later.
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
