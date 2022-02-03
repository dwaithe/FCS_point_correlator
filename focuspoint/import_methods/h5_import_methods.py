
import numpy as np
import tables
def print_children(group):
	"""Print all the sub-groups in `group` and leaf-nodes children of `group`.

	Parameters:
		group (pytables group): the group to be printed.
	"""
	for name, value in group._v_children.items():
		if isinstance(value, tables.Group):
			content = '(Group)'
		else:
			content = value.read()
		print(name)
		print('    Content:     %s' % content)
		print('    Description: %s\n' % value._v_title.decode())

def photon_hdf5_import(filepath):




	h5file = tables.open_file(filepath)
	print_children(h5file.root)
	print('photon_children',h5file.root)
	print_children(h5file.root.photon_data)
	photon_data = h5file.root.photon_data

	#%% Read the data
	timestamps = photon_data.timestamps.read()
	timestamps_unit = photon_data.timestamps_specs.timestamps_unit.read()
	detectors = photon_data.detectors.read()

	donor_ch = photon_data.measurement_specs.detectors_specs.spectral_ch1.read()
	acceptor_ch = photon_data.measurement_specs.detectors_specs.spectral_ch2.read()

	alex_period = photon_data.measurement_specs.alex_period.read()
	offset = photon_data.measurement_specs.alex_offset.read()
	donor_period = photon_data.measurement_specs.alex_excitation_period1.read()
	acceptor_period = photon_data.measurement_specs.alex_excitation_period2.read()

	#nanotimes = photon_data.nanotimes.read()


	#%% Print data summary
	print('Number of photons: %d' % timestamps.size)
	print('Timestamps unit:   %.2e seconds' % timestamps_unit)
	print('Detectors:         %s' % np.unique(detectors))
	print('Donor CH: %d     Acceptor CH: %d' % (donor_ch, acceptor_ch))
	print('ALEX period: %4d \nOffset: %4d \nDonor period: %s \nAcceptor period: %s' % \
		  (alex_period, offset, donor_period, acceptor_period))

	## Compute timestamp selections
	timestamps_donor = timestamps[detectors == donor_ch]
	timestamps_acceptor = timestamps[detectors == acceptor_ch]

	timestamps_mod = (timestamps - offset) % alex_period
	donor_excitation = (timestamps_mod < donor_period[1])*(timestamps_mod > donor_period[0])
	acceptor_excitation = (timestamps_mod < acceptor_period[1])*(timestamps_mod > acceptor_period[0])
	timestamps_Dex = timestamps[donor_excitation]
	timestamps_Aex = timestamps[acceptor_excitation]
	print('Timestamps',timestamps_mod,timestamps_Aex)

	chan_arr = []
	true_time_arr = []
	dtime_arr = []
	scalef = timestamps_unit/(1e-9)
	
	return np.array(detectors), np.array(timestamps).astype(np.float64)*scalef,np.array(timestamps_mod),timestamps_unit*1e9
