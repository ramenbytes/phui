#!/usr/bin/env python
# coding: utf-8

#### This file was originally a notebook from phconvert. As such it's contents
#### are under that project's license.

# File to be converted.
input_filename = 'data/0023uLRpitc_NTP_20dT_0.5GndCl.sm'
output_path = None  # Use None for saving in the same folder as the SM file


# # Default configuration

# Used when the metadata does not contain the field identity
default_identity = dict(
    author='Weiss Lab',
    author_affiliation='UCLA',
    creator='Antonino Ingargiola',
    creator_affiliation='UCLA')


# Used when the metadata does not contain the field setup
default_setup = dict(
    num_pixels = 2,
    num_spots = 1,
    num_spectral_ch = 2,
    num_polarization_ch = 1,
    num_split_ch = 1,
    modulated_excitation = True,
    lifetime = False,
    excitation_cw = [True, True],
    excitation_alternated=[True, True],
    excitation_wavelengths=[532e-9, 635e-9],
    detection_wavelengths=[580e-9, 660e-9]
)


# Used when the metadata does not contain the field measurement_specs
def_measurement_specs = dict(
    measurement_type = 'smFRET-usALEX',
    alex_period = 4000,
    alex_offset = 700,
    alex_excitation_period1 = (2180, 3900),
    alex_excitation_period2 = (200, 1800),
    detectors_specs = dict(spectral_ch1 = [0],
                           spectral_ch2 = [1]))


# # Imports

from pathlib import Path
import matplotlib.pyplot as plt
# interactive plots
plt.ion()
import yaml

import phconvert as phc
print('phconvert version: ' + phc.__version__)
# get_ipython().run_line_magic('matplotlib', 'inline')


# # Resolve paths

input_filename = Path(input_filename)
input_filename


assert input_filename.is_file(), 'Input SM file not found. Check the file name.'


if output_path is None:
    output_path = input_filename.parent

out_filename = Path(output_path, input_filename.stem + '.hdf5')
out_filename


# Create the output data folder if necessary
#out_filename.parent.mkdir(parents=True, exist_ok=True)


# # Load metadata

meta_filename = input_filename.with_suffix('.yml')
assert meta_filename.is_file(), 'Metadata YAML file not found.'


with open(str(meta_filename)) as f:
    metadata = yaml.load(f)
metadata


# # Preprocess timestamps

def update_with_defaults(input_dict, default_dict):
    for k in default_dict:
        if k not in input_dict:
            input_dict[k] = default_dict[k]
    return input_dict
            

def sm_load_photon_data(filename, metadata, def_measurement_specs):
    """Load photon_data from a .sm us-ALEX file into a metadata dict.
    """
    metadata = metadata.copy()
    timestamps, detectors, labels = phc.smreader.load_sm(str(filename),
                                                         return_labels=True)
    measurement_specs = metadata.pop('measurement_specs', def_measurement_specs)
    update_with_defaults(measurement_specs, def_measurement_specs)
            
    photon_data = dict(
        timestamps = timestamps,
        timestamps_specs = dict(timestamps_unit=12.5e-9),
        detectors = detectors,
        measurement_specs = measurement_specs)

    acquisition_duration = (timestamps[-1] - timestamps[0]) * 12.5e-9
    
    provenance = dict(
        filename=str(filename), 
        software='LabVIEW Data Acquisition usALEX')
    
    metadata.update(
        _filename = str(filename),
        acquisition_duration = round(acquisition_duration),
        photon_data = photon_data,
        provenance = provenance)
    return metadata


def fill_with_defaults(metadata, default_setup, default_identity):
    """Fill all missing values in metadata with defaults."""
    setup = metadata.get('setup', default_setup)
    metadata['setup'] = update_with_defaults(setup, default_setup)

    identity = metadata.get('identity', default_identity)
    metadata['identity'] = update_with_defaults(identity, default_identity)    
    
    sample = metadata['sample']
    sample['num_dyes'] = len(sample['dye_names'].split(','))


data = sm_load_photon_data(input_filename, metadata, def_measurement_specs)
fill_with_defaults(data, default_setup, default_identity)

## Dump now complete metadata to file, sans data file stuff. We do this for
## testing and dev work. Definitely not generalized, just a hack for now.
## Unironically stated on 06/18/20.

import copy # for deep copies

dump = copy.deepcopy(data)
del(dump['photon_data']['timestamps'])
del(dump['photon_data']['detectors'])

with open(os.path.expanduser('~/weisslab/gui/dumped.yaml'), mode='x') as f:
    yaml.dump(dump, stream=f, Dumper=yaml.Dumper)

phc.plotter.alternation_hist(data)


### Create Photon-HDF5

phc.hdf5.save_photon_hdf5(data, h5_fname=str(out_filename), overwrite=True, close=True)
