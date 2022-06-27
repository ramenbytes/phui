'''
A unified interface to phconvert's loading and conversion functionality.

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
import yaml
import phconvert as phc

import tempfile
# with open(os.path.expanduser('~/weisslab/phui/dumped.yml'), mode='r') as f:
#     # unsafe allows arbitrary code execution, meaning creation of numpy types
#     # can happen. Since we save a numpy float, this is desired here. Still, a hack.
#     snarf = yaml.unsafe_load(f)

def compose(g, f):
    '''Returns a one-argument function that applies f to the argument, then applies
g to that result and returns g's result.'''
    return lambda x: g(f(x))

def first_only(function):
    '''Returns a new, one argument function. When called, it will first apply the
    original function to the argument then extract the first element of that
    return value and return that. '''
    return compose(lambda x: x[0] ,function)

# these functions don't return a single dictionary, and for now we only want the
# first item of the returned tuple, which /is/ a single dictionary.
pq_loader = first_only(phc.loader.nsalex_pq)
bh_loader = first_only(phc.loader.nsalex_bh)

loaders = {'.sm' : phc.loader.usalex_sm,
           # TODO: Deal with (and expose?) the second, unmentioned dict that is
           # returned for picoquant files. It is currently unclear whether the
           # extra data would be of any use when converting to Photon-HDF5.
           '.ht3' : pq_loader,
           '.ptu' : pq_loader,
           '.pt3' : pq_loader,
           '.t3r' : phc.loader.nsalex_t3r,
           # TODO: Expose an interface for including the .set file. Could it be
           # done generally, for files that have extra data? HOFs?
           '.set' : bh_loader,
           '.spc' : bh_loader}

# FIXME: This function isn't very smart. It goes off the name of the file only
# right now. Could we make it smarter? Somehow check if the file really is the
# indicated file type.
def convertable_p(filename):
    '''If the filename designates a file of a convertable type, then return the
filename. Otherwise return False. Note that this function does not check
anything other than the /name/ of the file! You could take a PDF file, give it
the right file extension (say .sm), and this function will tell you it's A-OK to
try converting it!'''
    if extension(filename) in loaders:
        return filename
    else:
        return False

def extension(file):
    "Returns the extension of a file path"
    return os.path.splitext(file)[1]

# TODO: confirm which files didn't successfully convert without adding a
# description. This should be put in the documentation for the repository so
# that new users know what's happening when they try out the test files.
def load (file):
    '''General interface for loading the data from supported filetypes. Returns
    a dictionary containing the file data which may be passed to
    phconvert.hdf5.save_photon_hdf5(). It may be incomplete, for example it may
    not have a description if the file didn't, but it will not be malformed.'''
    return loaders[extension(file)](file)

def filename(file):
    "Returns the filename of a file path"
    return os.path.splitext(file)[0]

# To mitigate arbitrary code execution, we use the locked down loader by
# default. If users want the unsafe loader, they can change the variable.
#
# See here for details on depreciation of yaml.load()
# https://github.com/yaml/pyyaml/wiki/PyYAML-yaml.load(input)-Deprecation
# TODO: Document this variable for users to choose their safety level themselves.
yaml_loader = yaml.SafeLoader

# FIXME: for some reason, the "trace" test file does not successfully load with the
# high-level loaders. Says there is is a missing laser repetition rate in the
# metadata. Edge case to deal with later?

# /home/vir/weisslab/phui/data/trace_T2_300s_1_coincidence.ptu failed with
# missing laser repetition rate, and  nanodiamant_histo.phu failed because of a missing loader.

# TODO: Give better documentation for the yaml_loader variable. Make the
# interface less brittle and don't expose that we use pyaml?
def convert(input, *args, output=False, data_fragment=False, yml_file=False):
    '''Takes input file and converts it to Photon-HDF5, outputting to output. output
    defaults to input's value with the appropiate file type suffix.

    Two methods are available for augmenting the information provided by the
    experimental data in the input file.

    1) The yml_file arg:

        If yml_file is provided, it is assumed to be a file containing a
        fragment of the Photon-HDF5 data hierarchy in the form of yaml. The
        exception to this rule is the "/photon_data/measurement_specs" group,
        which may be specified as top-level item like in the example yml files.
        The contents will be loaded, and the resulting data destructively merged
        into the experimental data in the same manner that data_fragment is
        handled. To mitigate the danger of arbitrary code execution, pyaml's
        SafeLoader is used by default for loading the yaml file. If you wish to
        use a different method set the variable yaml_loader to a valid loader as
        specified by the pyaml docs.

    2) The data_fragment arg:

        If data_fragment is provided, it is interpreted as a piece of the
        Photon-HDF5 data hierarchy, with top-level entries corresponding to
        top-level Photon-HDF5 fields. The values it provides will be spliced
        into the data obtained from the photon data file, preserving any entries
        not explicitly provided. See recursive_merge() for more details.

    If both methods are specified, then both of the above processes will take
    place in the order they have been listed, so first the yaml file and then
    the data fragment. Since all of these merges are destructively recursive, if
    both the file and the fragment provide a value, then the fragment's value
    takes precedence.

    '''
    if not output:
        output = filename(input) + '.hdf5'

    data = load(input)
    yml_data = dict()

    if yml_file:
        with open(yml_file, mode='r') as f:
            yml_data = yaml.load(f, Loader=yaml_loader)
            # 26-June-2022: So it turns out that the yml files don't actually
            # mirror photon-hdf5 perfectly. In particular, the measurement_specs
            # group is sometimes specified at the top level. To my knowledge
            # this is the only instance of this, but I'm not hopeful.
            #
            # TODO: For now, we handle the one case we know of. At some point we
            # need to nail down a solid scheme to either handle all of the cases
            # or just tell the user that they will need to format their yml
            # files like the photon-hdf5.
            #
            # Fixup the yml data's hierarchy
            yml_data["photon_data"] = {"measurement_specs" : yml_data.pop("measurement_specs", dict())}
            # use the yaml file data to augment/overwrite info in the experimental data
            breakpoint()
            recursive_merge(yml_data, data)

    # use the provided fragment to overwrite/fill in fields
    if data_fragment:
        recursive_merge(data_fragment, data)

    ## FIXME: phconvert does not close hdf5 file on error! They aren't using a with-statement...
    try:
        (tmp_handle, tmp_name) = tempfile.mkstemp(prefix=filename(output) + "_temp",
                                              suffix=".hdf5",
                                              dir=os.path.dirname(output))
        # we only want the name, phconvert will do the opening and closing.
        os.close(tmp_handle)

        phc.hdf5.save_photon_hdf5(data, h5_fname=tmp_name, overwrite=True, close=True)
        # now that we have a successfull conversion, move our temp file to the
        # final destination
        os.rename(tmp_name, output)
    except:
        # delete the temp file when it isn't moved after a successful conversion
        os.remove(tmp_name)
        raise

    return

### Recursive merges are important for enabling user-specified YAML files to
### co-exist with metadata entered into the GUI by the user. It is also
### important if we wish to support YAML templates in the future.
###
### For the first instance, loading YAML files that the user specified can yield
### fragments of the Photon-HDF5 file structure. Each group is represented by a
### dictionary, so nested groups will be a dictionary within a dictionary
### (withing a dictionary....). Now, the user may not provide all the values for
### a group within the YAML file. That is, there could be "holes" in the
### Photon-HDF5 file structure that the user intends to fill in with the GUI. If
### the user fills in metadata in the GUI, then we will get another fragment of
### the file structure from that. What we need to be able to do is perform an OR
### operation between these two fragments, so that they are combined and the
### data entered through the GUI fills in all the "holes" in the data from the
### YAML file. But, what about conflicts? What if the user specifies something
### in the GUI that is also specified in the YAML file? In my opinion, it makes
### the most sense for the user's choice in the GUI to take precedence over what
### is in the YAML file. That provides the user a low-friction way of
### over-riding the values in the YAML file, which I thinks more sense then
### providing a high-friction way for the user to over-ride values provided in
### the GUI. In order to make all this happen, to OR together two fragments of
### Photon-HDF5 in dictionary form, we need to be able to merge two dictionaries
### in a special way. Given two dictionaries, we need to add all the
### dictionaries from one to the other, over-riding the receiving dictionary's
### entries when there is a conflict. However, if the conflict is between two
### entries which each hold dictionaries, then we want to merge those
### dictionaries as well, with the same override rules as before.

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
